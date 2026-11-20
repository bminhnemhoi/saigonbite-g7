' Update the table of contents and fields, save, and export a PDF with heading bookmarks.
' Usage: cscript //nologo docx2pdf.vbs <in.docx> <out.pdf>
Dim w, d
Set w = CreateObject("Word.Application")
w.Visible = False
w.DisplayAlerts = 0
Set d = w.Documents.Open(WScript.Arguments(0))
If d.TablesOfContents.Count > 0 Then d.TablesOfContents(1).Update
d.Fields.Update
If d.TablesOfContents.Count > 0 Then d.TablesOfContents(1).Update
d.Save
d.ExportAsFixedFormat WScript.Arguments(1), 17, False, 0, 0, 1, 1, 0, True, True, 1, True, True, False
d.Close False
w.Quit
