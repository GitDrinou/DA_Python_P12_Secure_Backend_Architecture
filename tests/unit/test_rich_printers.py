from cli import printers


def test_print_row_displays_table(capsys):
    printers.print_row(
        {"id": "emp_1", "name": "Alice", "role": "admin"},
        title="Employee",
    )
    output = capsys.readouterr().out

    assert "Employee" in output
    assert "id" in output
    assert "emp_1" in output
    assert "Alice" in output


def test_print_collection_displays_table(capsys):
    printers.print_collection(
        [
            {"id": "1", "name": "Alice"},
            {"id": "2", "name": "Bob"},
        ],
        title="Employees",
    )
    output = capsys.readouterr().out

    assert "Employees" in output
    assert "Alice" in output
    assert "Bob" in output


def test_print_success_displays_message(capsys):
    printers.print_success("Done")
    output = capsys.readouterr().out
    assert "SUCCESS" in output
    assert "Done" in output
