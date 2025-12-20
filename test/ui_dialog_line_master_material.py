# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_line_master_materialxztDFV.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QHeaderView, QSizePolicy, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MasterMaterial(object):
    def setupUi(self, MasterMaterial):
        if not MasterMaterial.objectName():
            MasterMaterial.setObjectName(u"MasterMaterial")
        MasterMaterial.resize(1041, 480)
        self.verticalLayout = QVBoxLayout(MasterMaterial)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(MasterMaterial)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.treeMaterial = QTreeWidget(self.widget)
        self.treeMaterial.setObjectName(u"treeMaterial")

        self.horizontalLayout.addWidget(self.treeMaterial, 0, Qt.AlignmentFlag.AlignLeft)

        self.tableDetail = QTableWidget(self.widget)
        if (self.tableDetail.columnCount() < 1):
            self.tableDetail.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableDetail.setHorizontalHeaderItem(0, __qtablewidgetitem)
        if (self.tableDetail.rowCount() < 15):
            self.tableDetail.setRowCount(15)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(0, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(1, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(2, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(3, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(4, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(5, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(6, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(7, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(8, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(9, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(10, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(11, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(12, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(13, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.tableDetail.setVerticalHeaderItem(14, __qtablewidgetitem15)
        self.tableDetail.setObjectName(u"tableDetail")

        self.horizontalLayout.addWidget(self.tableDetail)


        self.verticalLayout.addWidget(self.widget)

        self.buttonBox = QDialogButtonBox(MasterMaterial)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(MasterMaterial)
        self.buttonBox.accepted.connect(MasterMaterial.accept)
        self.buttonBox.rejected.connect(MasterMaterial.reject)

        QMetaObject.connectSlotsByName(MasterMaterial)
    # setupUi

    def retranslateUi(self, MasterMaterial):
        MasterMaterial.setWindowTitle(QCoreApplication.translate("MasterMaterial", u"Master Material", None))
        ___qtreewidgetitem = self.treeMaterial.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MasterMaterial", u"Material", None));
        ___qtablewidgetitem = self.tableDetail.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MasterMaterial", u"Value", None));
        ___qtablewidgetitem1 = self.tableDetail.verticalHeaderItem(0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MasterMaterial", u"Outer Diameter [m]", None));
        ___qtablewidgetitem2 = self.tableDetail.verticalHeaderItem(1)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MasterMaterial", u"Wet Weight [kg/m]", None));
        ___qtablewidgetitem3 = self.tableDetail.verticalHeaderItem(2)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MasterMaterial", u"Dry Weight [kg/m]", None));
        ___qtablewidgetitem4 = self.tableDetail.verticalHeaderItem(3)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MasterMaterial", u"EA [kN]", None));
        ___qtablewidgetitem5 = self.tableDetail.verticalHeaderItem(4)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MasterMaterial", u"EI [kN.m^2]", None));
        ___qtablewidgetitem6 = self.tableDetail.verticalHeaderItem(5)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MasterMaterial", u"Ci", None));
        ___qtablewidgetitem7 = self.tableDetail.verticalHeaderItem(6)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MasterMaterial", u"Cd", None));
        ___qtablewidgetitem8 = self.tableDetail.verticalHeaderItem(7)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MasterMaterial", u"GAE [N]", None));
        ___qtablewidgetitem9 = self.tableDetail.verticalHeaderItem(8)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MasterMaterial", u"GEI [N.m^2]", None));
        ___qtablewidgetitem10 = self.tableDetail.verticalHeaderItem(9)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MasterMaterial", u"GRHOL [kg/m]", None));
        ___qtablewidgetitem11 = self.tableDetail.verticalHeaderItem(10)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MasterMaterial", u"GRHOA [kg/m]", None));
        ___qtablewidgetitem12 = self.tableDetail.verticalHeaderItem(11)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MasterMaterial", u"GCI [N.m^2]", None));
        ___qtablewidgetitem13 = self.tableDetail.verticalHeaderItem(12)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MasterMaterial", u"GCD [kg/m]", None));
        ___qtablewidgetitem14 = self.tableDetail.verticalHeaderItem(13)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MasterMaterial", u"GAS [kg/m]", None));
        ___qtablewidgetitem15 = self.tableDetail.verticalHeaderItem(14)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MasterMaterial", u"BKTEN [N.m^2]", None));
    # retranslateUi

