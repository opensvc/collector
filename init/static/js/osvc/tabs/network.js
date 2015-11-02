function ips(divid, options)
{
    var o = {}

    // store parameters
    o.divid = divid
    o.direct_access_url = "R_IPS";
    o.div = $("#"+divid);
    o.nodes = options.nodes;

    o.ips_load = function()
    {
    	return ips_load(o);
    }

    o.div.load('/init/static/views/network.html', "", function() {
      ips_init(o);
    });
    
}

function ips_init(o)
{
	o.ips_ipv4_u = o.div.find("#ips_ipv4_u");
    o.ips_ipv6_u = o.div.find("#ips_ipv6_u");
    o.ips_ipv4_m = o.div.find("#ips_ipv4_m");
    o.ips_ipv6_m = o.div.find("#ips_ipv6_m");

    o.div.i18n();

 	o.ips_load();
}

function ips_build_table(o, resultset)
{
    
}

function ips_load(o)
{
    var th = "<tr><th>mac</th><th style='width:7em'>interface</th><th>type</th><th style='width:20em'>addr</th><th style='width:7em'>mask</th><th style='width:10em'>net name</th><th style='width:10em'>net comment</th><th style='width:4em'>net pvid</th><th>net base</th><th style='width:7em'>net gateway</th><th style='width:5em'>net prio</th><th style='width:7em'>net begin</th><th style='width:7em'>net end</th></tr>";

    services_osvcgetrest("R_IPS", [o.nodes],"", function(jd) {
      if (jd.data === undefined) {
        return;
      }

      o.ips_ipv4_u.html(th);
      o.ips_ipv6_u.html(th);
      o.ips_ipv4_m.html(th);
      o.ips_ipv6_m.html(th);

      var result = jd.data;
      // count
      var ipv4ucount=ipv6ucount=ipv4mcount=ipv6mcount=0;
      for(i=0;i<result.length;i++)
      {
        var resultset = result[i];
        if (!is_empty_or_null(resultset.net_name)) resultset.net_name = '-';
        if (!is_empty_or_null(resultset.net_comment)) resultset.net_comment = '-';
        if (!is_empty_or_null(resultset.net_pvid)) resultset.net_pvid = '-';
        if (!is_empty_or_null(resultset.net_network)) resultset.net_network = '-';
        if (!is_empty_or_null(resultset.net_gateway)) resultset.net_gateway = '-';
        if (!is_empty_or_null(resultset.prio)) resultset.prio = '-';
        if (!is_empty_or_null(resultset.net_begin)) resultset.net_begin = '-';
        if (!is_empty_or_null(resultset.net_end)) resultset.net_end = '-';
        var td ="<tr><td>";
        td += resultset.mac + "</td><td>";
        td += resultset.intf + "</td><td>";
        td += resultset.addr_type + "</td><td>";
        td += resultset.addr + "</td><td>";
        td += resultset.mask + "</td><td class='bluer'>";
        td += resultset.net_name + "</td><td class='bluer'>";
        td += resultset.net_comment + "</td><td class='bluer'>";
        td += resultset.net_pvid + "</td><td class='bluer'>";
        td += resultset.net_network + "</td><td class='bluer'>";
        td += resultset.net_gateway + "</td><td class='bluer'>";
        td += resultset.prio + "</td><td class='bluer'>";
        td += resultset.net_begin + "</td><td class='bluer'>";
        td += resultset.net_end;
        td += "</td></tr>";

        // Handle dispatch in array
        if (resultset.addr_type == "ipv4")
        {
            if (resultset.mask == "")
            {
                o.ips_ipv4_m.append(td);
                ipv4mcount+=1;
            }
            else
            {
                o.ips_ipv4_u.append(td);
                ipv4ucount+=1;
            }
        }
        else 
        {
            if (resultset.mask == "")
            {
                o.ips_ipv6_m.append(td);
                ipv6mcount+=1;
            }
            else
            {
                o.ips_ipv6_u.append(td);
                ipv6ucount+=1;
            }
        }
      }
        var emtpyline="<tr><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>";
        if (ipv4mcount==0) o.ips_ipv4_m.append(emtpyline);
        if (ipv4ucount==0) o.ips_ipv4_u.append(emtpyline);
        if (ipv6mcount==0) o.ips_ipv6_m.append(emtpyline);
        if (ipv6ucount==0) o.ips_ipv6_u.append(emtpyline);

    });
}