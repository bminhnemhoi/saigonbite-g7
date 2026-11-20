' Open each workbook in Excel, recalculate every formula and save (restores cached values and calcChain).
Dim xl, wb, i
Set xl = CreateObject("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
For i = 0 To WScript.Arguments.Count - 1
  Set wb = xl.Workbooks.Open(WScript.Arguments(i))
  xl.CalculateFull
  wb.Save
  wb.Close False
Next
xl.Quit
