# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LPLayersCreator
                                 A QGIS plugin
 This plugin creates a group of layers for digitising a drawing in the L - P Style
                              -------------------
        begin                : 2015-11-16
        git sha              : $Format:%H$
        copyright            : (C) 2015 by L - P Archaeology
        email                : m.johnson@lparchaeology.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
from qgis.core import *
# Import the code for the dialog
from layer_creator_dialog import LPLayersCreatorDialog
import os.path


class LPLayersCreator:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LPLayersCreator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LPLayersCreatorDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&L - P Layers Creator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LPLayersCreator')
        self.toolbar.setObjectName(u'LPLayersCreator')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LPLayersCreator', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LPLayersCreator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Create DWG Layers'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&L - P Layers Creator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # create layer
            vl = QgsVectorLayer("Point", "temporary_points", "memory")
            pr = vl.dataProvider()

            # add fields
            pr.addAttributes([QgsField("name", QVariant.String),
                                QgsField("age",  QVariant.Int),
                                QgsField("size", QVariant.Double)])
            vl.updateFields() # tell the vector layer to fetch changes from the provider

            # add a feature
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPoint(QgsPoint(10,10)))
            fet.setAttributes(["Johny", 2, 0.3])
            pr.addFeatures([fet])
            
            # update layer's extent when new features have been added
            # because change of extent in provider is not propagated to the layer
            vl.updateExtents()
            
            plugin_path = os.path.dirname(os.path.realpath(__file__))
            
            vl.loadNamedStyle(plugin_path + "/styles/L-P_spot_height.qml")

            
            QgsMapLayerRegistry.instance().addMapLayer(vl)
        
