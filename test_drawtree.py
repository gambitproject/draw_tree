"""
Test suite for drawtree module.

This module contains comprehensive tests for the game tree drawing functionality,
including unit tests for utility functions, integration tests for file processing,
and validation of TikZ output generation.
"""

import pytest
import tempfile
import os
from unittest.mock import patch

# Import the module under test
import drawtree


class TestUtilityFunctions:
    """Test utility functions for mathematical operations and formatting."""

    def test_fformat_default_places(self):
        """Test fformat with default 3 decimal places."""
        assert drawtree.fformat(3.14159) == "3.142"
        assert drawtree.fformat(3.0) == "3"
        assert drawtree.fformat(3.100) == "3.1"

    def test_fformat_custom_places(self):
        """Test fformat with custom decimal places."""
        assert drawtree.fformat(3.14159, 2) == "3.14"
        assert drawtree.fformat(3.14159, 0) == "3"
        assert drawtree.fformat(3.14159, 5) == "3.14159"

    def test_coord(self):
        """Test coordinate pair formatting."""
        assert drawtree.coord(1.0, 2.0) == "(1,2)"
        assert drawtree.coord(3.14, 2.71) == "(3.14,2.71)"
        assert drawtree.coord(-1.5, 0.0) == "(-1.5,0)"

    def test_twonorm(self):
        """Test Euclidean length calculation."""
        assert drawtree.twonorm([3, 4]) == 5.0
        assert drawtree.twonorm([1, 0]) == 1.0
        assert drawtree.twonorm([0, 0]) == 0.0

    def test_aeq(self):
        """Test almost equal comparison."""
        assert drawtree.aeq(1e-10, 0)  # Very small number should be considered zero
        assert drawtree.aeq(1.0, 1.0)
        assert not drawtree.aeq(1.0, 2.0)
        assert drawtree.aeq(1.0, 1.0 + 1e-10)  # Numbers within epsilon should be equal

    def test_degrees(self):
        """Test angle calculation in degrees."""
        import math
        assert abs(drawtree.degrees([1, 0]) - 0) < 1e-6
        assert abs(drawtree.degrees([0, 1]) - 90) < 1e-6
        assert abs(drawtree.degrees([-1, 0]) - 180) < 1e-6
        assert abs(drawtree.degrees([0, -1]) - (-90)) < 1e-6

    def test_stretch(self):
        """Test vector stretching to desired length."""
        result = drawtree.stretch([3, 4], 10)
        assert abs(drawtree.twonorm(result) - 10) < 1e-6
        assert abs(result[0] - 6) < 1e-6
        assert abs(result[1] - 8) < 1e-6

    def test_det(self):
        """Test determinant calculation."""
        assert drawtree.det(1, 2, 3, 4) == (1 * 4 - 2 * 3)
        assert drawtree.det(2, 0, 0, 3) == 6


class TestStringParsing:
    """Test string parsing functions."""

    def test_splitnumtext_basic(self):
        """Test basic number-text splitting."""
        assert drawtree.splitnumtext("2a") == (2.0, "a")
        assert drawtree.splitnumtext(".3xyz") == (0.3, "xyz")
        assert drawtree.splitnumtext("a") == (1, "a")
        assert drawtree.splitnumtext("22.2xyz") == (22.2, "xyz")

    def test_splitnumtext_edge_cases(self):
        """Test edge cases for number-text splitting."""
        assert drawtree.splitnumtext("") == (1, "")
        assert drawtree.splitnumtext("123") == (123.0, "")
        assert drawtree.splitnumtext(".") == (1, "")


class TestNodeOperations:
    """Test node-related operations."""

    def test_setnodeid(self):
        """Test node ID creation."""
        assert drawtree.setnodeid(1.0, "test") == "1,test"
        assert drawtree.setnodeid(0.5, "node") == "0.5,node"

    def test_cleannodeid(self):
        """Test node ID standardization."""
        # Mock the error function to avoid output during tests
        with patch('drawtree.error'):
            assert drawtree.cleannodeid("1,test") == "1,test"
            assert drawtree.cleannodeid("0.5,node") == "0.5,node"
            # Test error cases
            drawtree.cleannodeid("invalid")  # Should handle gracefully
            drawtree.cleannodeid("x,test")  # Invalid level


class TestOutputRoutines:
    """Test output and formatting functions."""

    def test_outall(self):
        """Test output stream printing."""
        test_stream = ["line1", "line2", "line3"]
        with patch('builtins.print') as mock_print:
            drawtree.outall(test_stream)
            assert mock_print.call_count == 3

    def test_outs(self):
        """Test single string output."""
        test_stream = []
        drawtree.outs("test", test_stream)
        assert test_stream == ["test"]

    def test_comment(self):
        """Test comment output."""
        with patch('drawtree.outs') as mock_outs:
            drawtree.comment("test comment")
            mock_outs.assert_called_with("%% test comment")


class TestFileOperations:
    """Test file reading and processing."""

    def test_readfile(self):
        """Test file reading with line processing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("line 1\n")
            f.write("  line 2 with spaces  \n")
            f.write("\n")  # Empty line
            f.write("line 3\n")
            temp_filename = f.name

        try:
            result = drawtree.readfile(temp_filename)
            expected = ["line 1", "line 2 with spaces", "line 3"]
            assert result == expected
        finally:
            os.unlink(temp_filename)

    def test_readfile_nonexistent(self):
        """Test file reading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            drawtree.readfile("nonexistent_file.txt")


class TestTikzGeneration:
    """Test TikZ code generation functions (legacy create_tikz_from_file)."""

    def test_create_tikz_from_file_basic(self):
        """Test basic TikZ code generation."""
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tex') as tikz_file:
            tikz_file.write("\\begin{tikzpicture}\n\\node at (0,0) {test};\n\\end{tikzpicture}")
            tikz_filename = tikz_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tex') as macro_file:
            macro_file.write("\\newcommand\\testmacro{value}\n% comment line\n\\newdimen\\testdim")
            macro_filename = macro_file.name

        try:
            result = drawtree.create_tikz_from_file(tikz_filename, macro_filename)
            
            # Verify the result contains expected components
            assert "\\usetikzlibrary{shapes}" in result
            assert "\\usetikzlibrary{arrows.meta}" in result
            assert "\\newcommand\\testmacro{value}" in result
            assert "\\newdimen\\testdim" in result
            assert "\\begin{tikzpicture}" in result
            assert "% comment line" not in result  # Comments should be filtered
            
        finally:
            os.unlink(tikz_filename)
            os.unlink(macro_filename)

    def test_create_tikz_from_file_missing_files(self):
        """Test TikZ generation with missing files."""
        with patch('builtins.print') as mock_print:
            result = drawtree.create_tikz_from_file("nonexistent.tex", "nonexistent_macro.tex")
            assert result == ""
            # Should print error message
            mock_print.assert_called()

    def test_create_tikz_from_file_missing_macros(self):
        """Test TikZ generation with missing macro file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tex') as tikz_file:
            tikz_file.write("\\begin{tikzpicture}\n\\end{tikzpicture}")
            tikz_filename = tikz_file.name

        try:
            with patch('builtins.print') as mock_print:
                result = drawtree.create_tikz_from_file(tikz_filename, "nonexistent_macro.tex")
                # Should still work but print warning
                assert "\\begin{tikzpicture}" in result
                mock_print.assert_called()
        finally:
            os.unlink(tikz_filename)


class TestCommandLineProcessing:
    """Test command-line argument processing."""

    def test_commandline_scale(self):
        """Test scale argument processing."""
        original_scale = drawtree.scale
        try:
            drawtree.commandline(["drawtree.py", "scale=2.5"])
            assert drawtree.scale == 2.5
        finally:
            drawtree.scale = original_scale

    def test_commandline_grid(self):
        """Test grid argument processing."""
        original_grid = drawtree.grid
        try:
            drawtree.commandline(["drawtree.py", "grid"])
            assert drawtree.grid is True
        finally:
            drawtree.grid = original_grid

    def test_commandline_file(self):
        """Test file argument processing."""
        original_ef_file = getattr(drawtree, 'ef_file', None)
        try:
            drawtree.commandline(["drawtree.py", "test_game.ef"])
            assert drawtree.ef_file == "test_game.ef"
        finally:
            if original_ef_file is not None:
                drawtree.ef_file = original_ef_file

    def test_commandline_invalid_scale(self):
        """Test invalid scale argument handling."""
        original_scale = drawtree.scale
        try:
            with patch('drawtree.outs') as mock_outs:
                drawtree.commandline(["drawtree.py", "scale=invalid"])
                # Should output error message
                mock_outs.assert_called()
                # Scale should remain unchanged
                assert drawtree.scale == original_scale
        finally:
            drawtree.scale = original_scale


class TestPlayerHandling:
    """Test player parsing and management."""

    def test_player_basic(self):
        """Test basic player parsing."""
        words = ["player", "1"]
        with patch('drawtree.defout'):
            p, advance = drawtree.player(words)
            assert p == 1
            assert advance == 2

    def test_player_with_name(self):
        """Test player parsing with name."""
        words = ["player", "2", "name", "Alice"]
        with patch('drawtree.defout'):
            p, advance = drawtree.player(words)
            assert p == 2
            assert advance == 4
            assert drawtree.playername[2] == "Alice"

    def test_player_invalid_number(self):
        """Test player parsing with invalid number."""
        words = ["player", "invalid"]
        with patch('drawtree.error') as mock_error:
            p, advance = drawtree.player(words)
            assert p == -1
            mock_error.assert_called()


class TestGeometryFunctions:
    """Test geometric operations for tree layout."""

    def test_isonlineseg_basic(self):
        """Test point-on-line-segment detection."""
        # Point on line segment
        assert drawtree.isonlineseg([0, 0], [1, 1], [2, 2]) is True
        # Point on line segment (slope 2)
        assert drawtree.isonlineseg([0, 0], [1, 2], [2, 4]) is True
        # Point not on line segment
        assert drawtree.isonlineseg([0, 0], [1, 3], [2, 4]) is False
        # Point at endpoint
        assert drawtree.isonlineseg([0, 0], [0, 0], [1, 1]) is True

    def test_makearc_basic(self):
        """Test arc generation."""
        # Test with simple coordinates
        result = drawtree.makearc([0, 0], [1, 0], [2, 0])
        assert isinstance(result, str)
        assert "arc(" in result


class TestDrawTreeFunction:
    """Test the new streamlined draw_tree function."""

    def test_draw_tree_basic(self):
        """Test basic draw_tree functionality."""
        # Create a simple .ef file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ef') as ef_file:
            ef_file.write("player 1\n")
            ef_file.write("level 0 node root player 1\n")
            ef_file.write("level 1 node left from 0,root player 2 payoffs 1 2\n")
            ef_file_path = ef_file.name

        # Create a simple macros file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tex') as macro_file:
            macro_file.write("\\newcommand\\testmacro{value}\n")
            macro_file.write("\\newdimen\\testdim\n")
            macro_file_path = macro_file.name

        try:
            result = drawtree.draw_tree(ef_file_path, macros_file_path=macro_file_path)
            
            # Verify the result contains expected components
            assert isinstance(result, str)
            assert len(result) > 0
            assert "\\usetikzlibrary{shapes}" in result
            assert "\\usetikzlibrary{arrows.meta}" in result
            assert "\\begin{tikzpicture}" in result
            assert "\\end{tikzpicture}" in result
            assert "\\newcommand\\testmacro{value}" in result
            assert "\\newdimen\\testdim" in result
            
        finally:
            os.unlink(ef_file_path)
            os.unlink(macro_file_path)

    def test_draw_tree_with_options(self):
        """Test draw_tree with different options."""
        # Create a simple .ef file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ef') as ef_file:
            ef_file.write("player 1\n")
            ef_file.write("level 0 node root player 1\n")
            ef_file_path = ef_file.name

        # Create a simple macros file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tex') as macro_file:
            macro_file.write("\\newcommand\\testmacro{value}\n")
            macro_file_path = macro_file.name

        try:
            # Test with scale
            result_scaled = drawtree.draw_tree(ef_file_path, scale_factor=2.0, macros_file_path=macro_file_path)
            assert "scale=2" in result_scaled
            
            # Test with grid
            result_grid = drawtree.draw_tree(ef_file_path, show_grid=True, macros_file_path=macro_file_path)
            assert "\\draw [help lines, color=green]" in result_grid
            
            # Test without grid (default)
            result_no_grid = drawtree.draw_tree(ef_file_path, show_grid=False, macros_file_path=macro_file_path)
            assert "% \\draw [help lines, color=green]" in result_no_grid
            
        finally:
            os.unlink(ef_file_path)
            os.unlink(macro_file_path)

    def test_draw_tree_missing_files(self):
        """Test draw_tree with missing files."""
        # Test with missing .ef file
        with pytest.raises(FileNotFoundError):
            drawtree.draw_tree("nonexistent.ef")

        # Test with missing macros file (should work but print warning)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ef') as ef_file:
            ef_file.write("player 1\nlevel 0 node root player 1\n")
            ef_file_path = ef_file.name

        try:
            with patch('builtins.print') as mock_print:
                result = drawtree.draw_tree(ef_file_path, macros_file_path="nonexistent_macros.tex")
                # Should still work but print warning
                assert "\\begin{tikzpicture}" in result
                mock_print.assert_called()
        finally:
            os.unlink(ef_file_path)


if __name__ == "__main__":
    pytest.main([__file__])