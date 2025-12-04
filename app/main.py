from fitgator.data.sqlite_repo import SQLiteRepository
from app.gui import FitGatorApp


def main() -> None:
    # Use SQLite as the persistence layer
    repo = SQLiteRepository("fitgator.db")

    # Launch the Tkinter GUI
    app = FitGatorApp(repo)
    app.mainloop()

    # Close DB connection cleanly on exit
    repo.close()


if __name__ == "__main__":
    main()
