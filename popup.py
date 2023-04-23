# starting from https://wiki.freecad.org/Macro_MessageBox
# for basic pop up window

from PySide import QtCore, QtGui
 
def tipsDialog(label, msg):
    # Create a simple dialog QMessageBox
    # The first argument indicates the icon used: one of QtGui.QMessageBox.{NoIcon, Information, Warning, Critical, Question} 
    diag = QtGui.QMessageBox(QtGui.QMessageBox.NoIcon, label, msg)
    diag.setWindowModality(QtCore.Qt.ApplicationModal)
    diag.exec_()
	#raise(Exception(msg))