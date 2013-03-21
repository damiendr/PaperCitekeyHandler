# Papers Citekey Handler

A simple helper for opening the PDF file associated with a [Papers2](http://www.papersapp.com/) universal citekey.

## Usage

- via a custom URL: clicking a link in the form `citekey://Author:2009iw` will open the corresponding PDF. Percent-encoded URLs also work: `citekey://Author%3A2009iw`

- via a text service: select the text `Author:2009iw` in any application, righ-click and choose "Open Paper PDF for Citekey" in the Services menu. Any spaces or `{}` characters around the citekey will be ignored, so selecting `{Author:2009iw}` works too.

I use this helper together with the Magic Citations feature of Papers2 and a modified [nvALT](http://brettterpstra.com/projects/nvalt/) which automatically creates a `citekey://` hyperlink for citekeys. Thus I can insert citekeys into plain-text notes by calling up Magic Citations, and open the associated PDF files simply by clicking on the citekeys.

## Installation

Simply copy PapersCitekeyHandler.app to `/Applications/` or to `~/Library/Services/`. There is no need to start the application explicitely. This is a background application with no settings.

To use the text service, first enable it in the Keyboard preference pane. One may need to log out and log back in for the service to appear in the menu.

## How it works

Most of the work is done by a Python script (open_citekey.py) that searches the Papers2 SQLite database located at `/Users/username/Library/Application Support/Papers2/Library.papers2/Database.papersdb` for papers matching the supplied citekey.

For details of citekey generation, see this document:
http://support.mekentosj.com/kb/read-write-cite/universal-citekey

The Python script is wrapped in a Cocoa background application that registers itself as a custom URL handler and as a text service.

## License

Note that this tool is not affiliated to or endorsed by the makers of the Papers2 app.