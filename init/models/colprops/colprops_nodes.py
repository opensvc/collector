nodes_cols = [
    'assetname',
    'fqdn',
    'serial',
    'manufacturer',
    'model',
    'bios_version',
    'sp_version',
    'asset_env',
    'role',
    'status',
    'type',
    'sec_zone',
    'tz',
    'loc_country',
    'loc_zip',
    'loc_city',
    'loc_addr',
    'loc_building',
    'loc_floor',
    'loc_room',
    'loc_rack',
    'enclosure',
    'enclosureslot',
    'hvvdc',
    'hvpool',
    'hv',
    'os_name',
    'os_release',
    'os_vendor',
    'os_arch',
    'os_kernel',
    'os_concat',
    'cpu_dies',
    'cpu_cores',
    'cpu_threads',
    'cpu_model',
    'cpu_freq',
    'mem_banks',
    'mem_slots',
    'mem_bytes',
    'listener_port',
    'version',
    'action_type',
    'collector',
    'connect_to',
    'node_env',
    'app',
    'team_responsible',
    'team_integ',
    'team_support',
    'power_supply_nb',
    'power_cabinet1',
    'power_cabinet2',
    'power_protect',
    'power_protect_breaker',
    'power_breaker1',
    'power_breaker2',
    'last_boot',
    'last_comm',
    'warranty_end',
    'maintenance_end',
    'os_obs_warn_date',
    'os_obs_alert_date',
    'hw_obs_warn_date',
    'hw_obs_alert_date',
    'updated',
]

nodes_colprops = {
    'id': HtmlTableColumn(
             field='id',
             table = 'nodes',
            ),
    'node_updated': HtmlTableColumn(
             field='node_updated',
             table = 'nodes',
            ),
    'updated': HtmlTableColumn(
             field='updated',
             table = 'nodes',
            ),
    'loc_country': HtmlTableColumn(
             field='loc_country',
             table = 'nodes',
            ),
    'loc_zip': HtmlTableColumn(
             field='loc_zip',
             table = 'nodes',
            ),
    'loc_city': HtmlTableColumn(
             field='loc_city',
             table = 'nodes',
            ),
    'loc_addr': HtmlTableColumn(
             field='loc_addr',
             table = 'nodes',
            ),
    'loc_building': HtmlTableColumn(
             field='loc_building',
             table = 'nodes',
            ),
    'loc_floor': HtmlTableColumn(
             field='loc_floor',
             table = 'nodes',
            ),
    'loc_room': HtmlTableColumn(
             field='loc_room',
             table = 'nodes',
            ),
    'loc_rack': HtmlTableColumn(
             field='loc_rack',
             table = 'nodes',
            ),
    'os_concat': HtmlTableColumn(
             field='os_concat',
             table = 'nodes',
            ),
    'os_name': HtmlTableColumn(
             field='os_name',
             table = 'nodes',
            ),
    'os_release': HtmlTableColumn(
             field='os_release',
             table = 'nodes',
            ),
    'os_vendor': HtmlTableColumn(
             field='os_vendor',
             table = 'nodes',
            ),
    'os_arch': HtmlTableColumn(
             field='os_arch',
             table = 'nodes',
            ),
    'os_kernel': HtmlTableColumn(
             field='os_kernel',
             table = 'nodes',
            ),
    'cpu_vendor': HtmlTableColumn(
             field='cpu_vendor',
             table = 'nodes',
            ),
    'cpu_dies': HtmlTableColumn(
             field='cpu_dies',
             table = 'nodes',
            ),
    'cpu_cores': HtmlTableColumn(
             field='cpu_cores',
             table = 'nodes',
            ),
    'last_boot': HtmlTableColumn(
             field='last_boot',
             table = 'nodes',
            ),
    'last_comm': HtmlTableColumn(
             field='last_comm',
             table = 'nodes',
            ),
    'sec_zone': HtmlTableColumn(
             field='sec_zone',
             table = 'nodes',
            ),
    'cpu_threads': HtmlTableColumn(
             field='cpu_threads',
             table = 'nodes',
            ),
    'cpu_model': HtmlTableColumn(
             field='cpu_model',
             table = 'nodes',
            ),
    'cpu_freq': HtmlTableColumn(
             field='cpu_freq',
             table = 'nodes',
            ),
    'mem_banks': HtmlTableColumn(
             field='mem_banks',
             table = 'nodes',
            ),
    'mem_slots': HtmlTableColumn(
             field='mem_slots',
             table = 'nodes',
            ),
    'mem_bytes': HtmlTableColumn(
             field='mem_bytes',
             table = 'nodes',
            ),
    'nodename': HtmlTableColumn(
             field='nodename',
             table = 'nodes',
            ),
    'tz': HtmlTableColumn(
             field='tz',
             table = 'nodes',
            ),
    'collector': HtmlTableColumn(
             field='collector',
             table = 'nodes',
            ),
    'connect_to': HtmlTableColumn(
             field='connect_to',
             table = 'nodes',
            ),
    'version': HtmlTableColumn(
             field='version',
             table = 'nodes',
            ),
    'action_type': HtmlTableColumn(
             field='action_type',
             table = 'nodes',
            ),
    'listener_port': HtmlTableColumn(
             field='listener_port',
             table = 'nodes',
            ),
    'assetname': HtmlTableColumn(
             field='assetname',
             table = 'nodes',
            ),
    'fqdn': HtmlTableColumn(
             field='fqdn',
             table = 'nodes',
            ),
    'hvvdc': HtmlTableColumn(
             field='hvvdc',
             table = 'nodes',
            ),
    'hvpool': HtmlTableColumn(
             field='hvpool',
             table = 'nodes',
            ),
    'hv': HtmlTableColumn(
             field='hv',
             table = 'nodes',
            ),
    'enclosure': HtmlTableColumn(
             field='enclosure',
             table = 'nodes',
            ),
    'enclosureslot': HtmlTableColumn(
             field='enclosureslot',
             table = 'nodes',
            ),
    'serial': HtmlTableColumn(
             field='serial',
             table = 'nodes',
            ),
    'sp_version': HtmlTableColumn(
             field='sp_version',
             table = 'nodes',
            ),
    'bios_version': HtmlTableColumn(
             field='bios_version',
             table = 'nodes',
            ),
    'manufacturer': HtmlTableColumn(
             field='manufacturer',
             table = 'nodes',
            ),
    'model': HtmlTableColumn(
             field='model',
             table = 'nodes',
            ),
    'team_responsible': HtmlTableColumn(
             field='team_responsible',
             table = 'nodes',
            ),
    'team_integ': HtmlTableColumn(
             field='team_integ',
             table = 'nodes',
            ),
    'team_support': HtmlTableColumn(
             field='team_support',
             table = 'nodes',
            ),
    'app': HtmlTableColumn(
             field='app',
             table = 'nodes',
            ),
    'role': HtmlTableColumn(
             field='role',
             table = 'nodes',
            ),
    'node_env': HtmlTableColumn(
             field='node_env',
             table = 'nodes',
            ),
    'asset_env': HtmlTableColumn(
             field='asset_env',
             table = 'nodes',
            ),
    'warranty_end': HtmlTableColumn(
             field='warranty_end',
             table = 'nodes',
            ),
    'os_obs_warn_date': HtmlTableColumn(
             field='os_obs_warn_date',
             table = 'nodes',
            ),
    'os_obs_alert_date': HtmlTableColumn(
             field='os_obs_alert_date',
             table = 'nodes',
            ),
    'hw_obs_warn_date': HtmlTableColumn(
             field='hw_obs_warn_date',
             table = 'nodes',
            ),
    'hw_obs_alert_date': HtmlTableColumn(
             field='hw_obs_alert_date',
             table = 'nodes',
            ),
    'maintenance_end': HtmlTableColumn(
             field='maintenance_end',
             table = 'nodes',
            ),
    'status': HtmlTableColumn(
             field='status',
             table = 'nodes',
            ),
    'type': HtmlTableColumn(
             field='type',
             table = 'nodes',
            ),
    'power_supply_nb': HtmlTableColumn(
             field='power_supply_nb',
             table = 'nodes',
            ),
    'power_cabinet1': HtmlTableColumn(
             field='power_cabinet1',
             table = 'nodes',
            ),
    'power_cabinet2': HtmlTableColumn(
             field='power_cabinet2',
             table = 'nodes',
            ),
    'power_protect': HtmlTableColumn(
             field='power_protect',
             table = 'nodes',
            ),
    'power_protect_breaker': HtmlTableColumn(
             field='power_protect_breaker',
             table = 'nodes',
            ),
    'power_breaker1': HtmlTableColumn(
             field='power_breaker1',
             table = 'nodes',
            ),
    'power_breaker2': HtmlTableColumn(
             field='power_breaker2',
             table = 'nodes',
            ),
}

node_hba_colprops = {
    'nodename': HtmlTableColumn(
             table='node_hba',
             field='nodename',
            ),
    'hba_id': HtmlTableColumn(
             table='node_hba',
             field='hba_id',
            ),
    'hba_type': HtmlTableColumn(
             table='node_hba',
             field='hba_type',
            ),
    'disk_updated': HtmlTableColumn(
             table='node_hba',
             field='updated',
            ),
}


