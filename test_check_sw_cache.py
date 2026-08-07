# -*- coding: utf-8 -*-
"""Service Worker のキャッシュ更新漏れを検出するゲートのテスト。

空ページ問題の主因は SW キャッシュ。ASSETS を足したのに CACHE_NAME を上げないと、
既存の訪問者には古いキャッシュが返り続けて新ツールが表示されない。
これまでこの手順は plan の文章と人間の注意力だけで守られていた。
"""
import importlib.util
import sys
from pathlib import Path

_MOD_PATH = Path(__file__).resolve().parent / "check_sw_cache.py"
_spec = importlib.util.spec_from_file_location("csc", _MOD_PATH)
csc = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = csc
_spec.loader.exec_module(csc)

_SW = """const CACHE_NAME = 'ddx-tools-v94';
const ASSETS = [
  './',
  './index.html',
  './aki.html',
];
self.addEventListener('install', () => {});
"""


# --- 解析 --------------------------------------------------------------------
def test_parses_cache_name():
    assert csc.parse_cache_name(_SW) == "ddx-tools-v94"


def test_parses_double_quoted_cache_name():
    assert csc.parse_cache_name('const CACHE_NAME = "ddx-tools-v7";') == "ddx-tools-v7"


def test_missing_cache_name_is_none():
    assert csc.parse_cache_name("const X = 1;") is None


def test_parses_assets():
    assert csc.parse_assets(_SW) == ["./", "./index.html", "./aki.html"]


def test_assets_stop_at_closing_bracket():
    """ASSETS の後ろにある fetch ハンドラ内の文字列を巻き込まない。"""
    assert "self" not in "".join(csc.parse_assets(_SW))


def test_version_number_is_extracted():
    assert csc.version_of("ddx-tools-v94") == 94


def test_version_of_unversioned_name_is_none():
    assert csc.version_of("ddx-tools") is None


# --- ASSETS の実在と網羅 ------------------------------------------------------
def test_asset_pointing_to_missing_file_is_reported():
    assert csc.missing_assets(["./index.html", "./gone.html"], {"index.html"}) == ["./gone.html"]


def test_directory_root_asset_is_not_treated_as_missing():
    assert csc.missing_assets(["./"], set()) == []


def test_page_absent_from_assets_is_reported():
    assert csc.unlisted_pages({"index.html", "newtool.html"}, ["./index.html"]) == ["newtool.html"]


def test_fully_listed_pages_report_nothing():
    assert csc.unlisted_pages({"index.html"}, ["./index.html"]) == []


# --- CACHE_NAME 上げ忘れ ------------------------------------------------------
def test_changed_assets_without_bump_is_flagged():
    assert csc.needs_bump(["./a.html"], ["./a.html", "./b.html"], 94, 94) is True


def test_changed_assets_with_bump_is_fine():
    assert csc.needs_bump(["./a.html"], ["./a.html", "./b.html"], 94, 95) is False


def test_unchanged_assets_need_no_bump():
    assert csc.needs_bump(["./a.html"], ["./a.html"], 94, 94) is False


def test_removed_asset_also_requires_bump():
    assert csc.needs_bump(["./a.html", "./b.html"], ["./a.html"], 94, 94) is True


def test_decreasing_version_is_flagged():
    assert csc.needs_bump(["./a.html"], ["./a.html", "./b.html"], 94, 93) is True


# --- 判定 --------------------------------------------------------------------
def test_exit_zero_when_everything_is_consistent():
    assert csc.decide_exit(missing=0, unlisted=0, bump_needed=False, compared=True) == 0


def test_exit_one_when_bump_missing():
    assert csc.decide_exit(missing=0, unlisted=0, bump_needed=True, compared=True) == 1


def test_exit_one_on_missing_asset():
    assert csc.decide_exit(missing=1, unlisted=0, bump_needed=False, compared=True) == 1


def test_exit_one_on_unlisted_page():
    assert csc.decide_exit(missing=0, unlisted=1, bump_needed=False, compared=True) == 1


def test_exit_two_when_git_comparison_unavailable():
    """HEAD と比較できなければ上げ忘れは判定できない。合格を主張しない。"""
    assert csc.decide_exit(missing=0, unlisted=0, bump_needed=False, compared=False) == 2
