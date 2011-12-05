/*
###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2010, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
*/

(function(){

var ZC = Ext.ns('Zenoss.component');

function render_link(ob) {
    if (ob && ob.uid) {
        return Zenoss.render.link(ob.uid);
    } else {
        return ob;
    }
}

ZC.JavaAppPanel = Ext.extend(ZC.ComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'JavaApp',
            fields: [
              	{name: 'uid'},
                {name: 'severity'},
                {name: 'status'},
                {name: 'name'},
                {name: 'javaPort'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                width: 60
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                sortable: true
            },{
                id: 'javaPort',
                dataIndex: 'javaPort',
                header: _t('Port'),
                sortable: true,
                width: 150
            },{
                id: 'status',
                dataIndex: 'status',
                header: _t('Status'),
                sortable: true,
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                sortable: true,
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                sortable: true,
            }
			] 
        });
        ZC.JavaAppPanel.superclass.constructor.call(this, config);
    }
});

Ext.reg('JavaAppPanel', ZC.JavaAppPanel);
ZC.registerName('JavaApp', _t('Java App'), _t('Java Apps'));

})();

