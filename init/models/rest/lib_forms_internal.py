from gluon.storage import Storage

form_data_internal = [
    Storage({
        "id": -1,
        "form_name": "internal_add_contextual_thresholds",
        "form_folder": "/internal",
        "form_type": "generic",
        "form_definition": {
            "Vertical": True,
            "Outputs": [
                {
                    "Type": "json",
                    "Format": "dict",
                    "Dest": "rest",
                    "Function": "/checks/contextual_settings",
                    "Handler": "POST"
                }
            ],
            "Inputs": [
                {
                    "Id": "chk_type",
                    "Label": "Type",
                    "LabelCss": "check16",
                    "Type": "string",
                    "Mandatory": True,
                    "Function": "/checks/live",
                    "Args": [
                        "props = chk_type",
                        "groupby = chk_type",
                        "orderby = chk_type",
                        "meta = 0",
                        "limit = 0"
                    ],
                    "DisableAutoDefault": True
                },
                {
                    "Id": "chk_instance",
                    "Label": "Instance regex",
                    "LabelCss": "check16",
                    "Type": "string",
                    "Mandatory": True
                },
                {
                    "Id": "chk_low",
                    "Label": "Low threshold",
                    "LabelCss": "fa-step-backward",
                    "Type": "integer",
                    "Constraint": "match [0-9]*"
                },
                {
                    "Id": "chk_high",
                    "Label": "High threshold",
                    "LabelCss": "fa-step-forward",
                    "Type": "integer",
                    "Constraint": "match [0-9]*"
                },
                {
                    "Id": "fset_id",
                    "Label": "Filterset",
                    "LabelCss": "filter16",
                    "Type": "string",
                    "Mandatory": True,
                    "Function": "/filtersets",
                    "Args": [
                        "props = id,fset_name",
                        "orderby = fset_name",
                        "meta = 0",
                        "limit = 0"
                    ],
                    "Value": "#id",
                    "Format": "#fset_name",
                    "DisableAutoDefault": True
                },
            ]
        }
    }),
    Storage({
        "id": -2,
        "form_name": "internal_add_dns_record",
        "form_folder": "/internal",
        "form_type": "generic",
        "form_definition": {
            "Outputs": [
                {
                    "Dest": "rest",
                    "Function": "/dns/records",
                    "Handler": "POST",
                    "Type": "json",
                    "Format": "dict"
                }
            ],
            "Vertical": True,
            "Css": "dns48",
            "Inputs": [
                {
                    "Mandatory": True,
                    "DisplayModeLabel": "name",
                    "LabelCss": "dns16",
                    "Label": "Name",
                    "Type": "string",
                    "Id": "name"
                },
                {
                    "Function": "/dns/domains",
                    "Mandatory": True,
                    "Format": "#name",
                    "Args": [
                        "props = id,name",
                        "limit = 0",
                        "meta = 0",
                        "orderby = name"
                    ],
                    "Value": "#id",
                    "DisplayModeLabel": "zone",
                    "LabelCss": "dns16",
                    "Label": "Domain",
                    "Type": "string",
                    "Id": "domain_id"
                },
                {
                    "Default": 120,
                    "Label": "TTL",
                    "DisplayModeLabel": "ttl",
                    "LabelCss": "dns16",
                    "ExpertMode": True,
                    "Type": "integer",
                    "Id": "ttl"
                },
                {
                    "Default": 0,
                    "Label": "Priority",
                    "DisplayModeLabel": "prio",
                    "LabelCss": "dns16",
                    "ExpertMode": True,
                    "Type": "integer",
                    "Id": "prio"
                },
                {
                    "Mandatory": True,
                    "Default": "A",
                    "Label": "Type",
                    "Candidates": [
                        "A",
                        "AAAA",
                        "A6",
                        "CNAME",
                        "DNAME",
                        "DNSKEY",
                        "DS",
                        "HINFO",
                        "ISDN",
                        "KEY",
                        "LOC",
                        "MX",
                        "NAPTR",
                        "NS",
                        "NSEC",
                        "PTR",
                        "SOA",
                        "SRV",
                        "TXT"
                    ],
                    "LabelCss": "dns16",
                    "DisplayModeLabel": "type",
                    "Type": "string",
                    "Id": "type"
                },
                {
                    "Function": "/networks",
                    "Mandatory": False,
                    "Format": "#name (#network/#netmask)",
                    "Args": [
                        "props = id,name,network,netmask",
                        "limit = 0",
                        "meta = 0",
                        "orderby = name"
                    ],
                    "Value": "#id",
                    "DisplayModeLabel": "network",
                    "LabelCss": "net16",
                    "Label": "Network",
                    "Type": "string",
                    "Id": "network",
                    "Condition": "#type == A"
                },
                {
                    "Label": "Content",
                    "Key": "content",
                    "LabelCss": "dns16",
                    "DisplayModeLabel": "content",
                    "Type": "string",
                    "Id": "content_not_a",
                    "Condition": "#type != A"
                },
                {
                    "Function": "/networks/#network/ips",
                    "Format": "#ip (t:#type n:#nodename r:#record_name)",
                    "Args": [
                        "props = ip,type,nodename,record_name"
                    ],
                    "Value": "#ip",
                    "DisplayModeLabel": "content",
                    "Key": "content",
                    "LabelCss": "dns16",
                    "Label": "Content",
                    "Type": "string",
                    "Id": "content_a",
                    "Condition": "#type == A"
                }
            ]
        },
    }),
    Storage({
        "id": -3,
        "form_name": "internal_add_network_segment",
        "form_folder": "/internal",
        "form_type": "generic",
        "form_definition": {
            "Outputs": [
                {
                    "Dest": "rest",
                    "Function": "/networks/#net_id/segments",
                    "Handler": "POST",
                    "Type": "json",
                    "Format": "dict"
                }
            ],
            "Css": "net16 fa-2x",
            "Inputs": [
                {
                    "Mandatory": True,
                    "Default": "static",
                    "StrictCandidates": True,
                    "DisplayModeLabel": "type",
                    "Candidates": [
                        "static",
                        "dynamic"
                    ],
                    "LabelCss": "net16",
                    "Label": "Type",
                    "Id": "seg_type"
                },
                {
                    "Function": "/networks",
                    "Mandatory": True,
                    "Format": "#name #network/#netmask",
                    "Args": [
                        "props = id,name,network,netmask",
                        "limit = 0",
                        "meta = 0",
                        "orderby = network"
                    ],
                    "Value": "#id",
                    "DisplayModeLabel": "network",
                    "LabelCss": "net16",
                    "Label": "Network",
                    "Type": "integer",
                    "Id": "net_id"
                },
                {
                    "Label": "Begin",
                    "DisplayModeLabel": "begin",
                    "Type": "string",
                    "Id": "seg_begin",
                    "LabelCss": "net16"
                },
                {
                    "Label": "End",
                    "DisplayModeLabel": "end",
                    "Type": "string",
                    "Id": "seg_end",
                    "LabelCss": "net16"
                }
            ]
        },
    }),
    Storage({
        "id": -4,
        "form_name": "internal_add_quota",
        "form_folder": "/internal",
        "form_type": "generic",
        "form_definition": {
            "Outputs": [
                {
                    "Function": "/arrays/#array_id/diskgroups/#dg_id/quotas",
                    "Format": "dict",
                    "Keys": [
                        "app_id",
                        "quota"
                    ],
                    "Dest": "rest",
                    "Handler": "POST",
                    "Type": "json"
                }
            ],
            "Css": "disk48",
            "Inputs": [
                {
                    "Function": "/arrays",
                    "Mandatory": True,
                    "DisableAutoDefault": True,
                    "Format": "#array_name",
                    "Args": [
                        "props = array_name,id",
                        "limit = 0",
                        "meta = 0",
                        "orderby = array_name",
                        "filters = array_model !vdisk%"
                    ],
                    "Value": "#id",
                    "DisplayModeLabel": "array",
                    "LabelCss": "hd16",
                    "Label": "Array",
                    "Type": "string",
                    "Id": "array_id"
                },
                {
                    "Function": "/arrays/#array_id/diskgroups",
                    "Mandatory": True,
                    "Format": "#dg_name",
                    "Args": [
                        "props = dg_name,id",
                        "limit = 0",
                        "meta = 0",
                        "orderby = dg_name"
                    ],
                    "Value": "#id",
                    "DisplayModeLabel": "diskgroup",
                    "LabelCss": "hd16",
                    "Label": "Diskgroup",
                    "Type": "string",
                    "Id": "dg_id",
                    "Condition": "#array_id > 0"
                },
                {
                    "Function": "/apps",
                    "DisableAutoDefault": True,
                    "Mandatory": True,
                    "Format": "#app",
                    "Args": [
                        "props = id,app",
                        "limit = 0",
                        "meta = 0",
                        "orderby = app"
                    ],
                    "Value": "#id",
                    "DisplayModeLabel": "app",
                    "LabelCss": "svc",
                    "Label": "App",
                    "Type": "string",
                    "Id": "app_id"
                },
                {
                    "Mandatory": True,
                    "DisplayModeLabel": "quota",
                    "LabelCss": "hd16",
                    "Label": "Quota",
                    "Type": "integer",
                    "Id": "quota",
                    "Unit": "mb"
                }
            ]
        },
    }),
    Storage({
        "id": -5,
        "form_name": "internal_add_default_thresholds",
        "form_folder": "/internal",
        "form_type": "generic",
        "form_definition": {
            "Vertical": True,
            "Outputs": [
                {
                    "Type": "json",
                    "Format": "dict",
                    "Dest": "rest",
                    "Function": "/checks/defaults",
                    "Handler": "POST"
                }
            ],
            "Inputs": [
                {
                    "Id": "chk_type",
                    "Label": "Type",
                    "LabelCss": "check16",
                    "Type": "string",
                    "Mandatory": True,
                    "Function": "/checks/live",
                    "Args": [
                        "props = chk_type",
                        "groupby = chk_type",
                        "orderby = chk_type",
                        "meta = 0",
                        "limit = 0"
                    ],
                    "DisableAutoDefault": True
                },
                {
                    "Id": "chk_inst",
                    "Label": "Instance regex",
                    "LabelCss": "check16",
                    "Type": "string",
                    "Mandatory": True
                },
                {
                    "Id": "chk_prio",
                    "Label": "Priority",
                    "LabelCss": "fa-sort",
                    "Type": "integer",
                    "Constraint": "match [0-9]*"
                },
                {
                    "Id": "chk_low",
                    "Label": "Low threshold",
                    "LabelCss": "fa-step-backward",
                    "Type": "integer",
                    "Constraint": "match [0-9]*"
                },
                {
                    "Id": "chk_high",
                    "Label": "High threshold",
                    "LabelCss": "fa-step-forward",
                    "Type": "integer",
                    "Constraint": "match [0-9]*"
                },
            ]
        }
    }),
]

def get_internal_form(form_id):
    for form in form_data_internal:
        if form_id == form["id"]:
            return form

