//MD 27082015
// Wiki function

function wiki(divid, options)
{
    var o = {}

    // store parameters
    o.divid = divid

    o.direct_access_url = "R_WIKI";
    o.div = $("#"+divid);
    o.nodes = options.nodes;

    o.wiki_insert_sign = function(){
      return wiki_insert_sign(this)
    }

    o.wiki_help = function() {
    	return wiki_help(this);
    }

    o.wiki_save = function()
    {
    	return wiki_save(this);
    }

    o.wiki_switch_edit = function()
    {
    	return wiki_switch_edit(this);
    }

    o.div.load('/init/static/views/wiki.html', "", function() {
      wiki_init(o);
    });
    
}

function wiki_init(o)
{
	o.wiki_table_last_changes = o.div.find("#wiki_table_last_changes");
    o.wiki_save_button = o.div.find("#wiki_save_button");
    o.wiki_help_button = o.div.find("#wiki_help_button");
    o.wiki_insert_button = o.div.find("#wiki_insert_button")
    o.wiki_edit_button = o.div.find("#wiki_edit_button");

    o.wiki_tab_show = o.div.find("#wiki_tab_show");
    o.wiki_edit = o.div.find("#wiki_edit");
    o.wiki_editor = o.div.find("#wiki_editor");
    o.wiki_tab_insert = o.div.find("#wiki_tab_insert");

    o.wiki_tab_ins = o.div.find("#wiki_tab_ins");
    o.wiki_tab_res = o.div.find("#wiki_tab_res");

    o.wiki_table_last_changes = o.div.find("#wiki_table_last_changes");

    o.wiki_messages = o.div.find("#wiki_messages");
    o.wiki_tab_titles = o.div.find("#wiki_tab_title");

    o.wiki_save_button.on("click", function () {
    	o.wiki_save();
    });

    o.wiki_help_button.on("click", function () {
    	o.wiki_help();
    });

    o.wiki_insert_button.on("click", function () {
    	o.wiki_insert_sign();
    });

    o.wiki_edit_button.on("click", function () {
    	o.wiki_switch_edit();
    });

	services_osvcgetrest("R_WIKI", [o.nodes],"", function(jd) {
      if (jd.data === undefined) {
      	o.wiki_messages.html("No response...");
        return;
      }
      o.wiki_messages.html('');
      var result=jd.data;
     
      for (i=0;i<result.length;i++)
      {
      	if (i < 5) {
      		var line = "<tr><td>" + result[i].saved_on + "</td><td>"+ result[i].email +"</td></tr>";
      		o.wiki_table_last_changes.append(line);
      	}
      	else
      		break;
      }
      o.wiki_tab_titles.html("Last " + i + " result(s)");

      var converter = new Markdown.Converter();
      for(i=result.length-1;i>=0;i--)
      {
      	o.wiki_tab_show.append(converter.makeHtml(result[i].body));
      }

    });
}

function wiki_switch_edit(o)
{
	o.wiki_tab_show.hide();
	o.wiki_tab_insert.show();
	o.wiki_edit.hide();
	o.wiki_editor.show();
}

function wiki_help(o)
{
	toggle("wiki_syntax");
}

function wiki_save(o)
{
	var value = o.wiki_tab_ins.val();
	services_osvcpostrest("R_WIKI", [o.nodes], "", {"body": value}, function(jd) {
      if (jd.data === undefined) {
      	$('#wiki_messages').html("No response...");
        return
      }
      $('#wiki_messages').html(jd.info);
      
    },function() {});
}

function wiki_insert_sign(o)
{
  jQuery.fn.extend({
  insertAtCaret: function(myValue){
    return this.each(function(i) {
      if (document.selection) {
        //For browsers like Internet Explorer
        this.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
        this.focus();
      }
      else if (this.selectionStart || this.selectionStart == '0') {
        //For browsers like Firefox and Webkit based
        var startPos = this.selectionStart;
        var endPos = this.selectionEnd;
        var scrollTop = this.scrollTop;
        this.value = this.value.substring(0,startPos)+myValue+this.value.substring(endPos,this.value.length);
        this.focus();
        this.selectionStart = startPos + myValue.length;
        this.selectionEnd = startPos + myValue.length;
        this.scrollTop = scrollTop;
      } else {
        this.value += myValue;
        this.focus();
      }
    })
  }
  });
  var currentTime = new Date()
  var day = currentTime.getDate()
  var month = currentTime.getMonth()+1
  var year = currentTime.getFullYear()
  var hours = currentTime.getHours()
  var minutes = currentTime.getMinutes()
  if (month<10) { month = "0"+month }
  if (day<10) { day = "0"+day }
  if (hours<10) { hours = "0"+hours }
  if (minutes<10) { minutes = "0"+minutes }
  var ds = day+"-"+month+"-"+year+" "+hours+":"+minutes
  o.wiki_tab_ins.insertAtCaret("*" + ds + " " +  _self.first_name + " " + _self.last_name);
}