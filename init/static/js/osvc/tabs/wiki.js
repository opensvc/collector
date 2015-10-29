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
    o.div.load('/init/static/views/wiki.html', "", function() {
      ;
    });

    o.wiki_init = function(){
      return wiki_init(this)
    }

    o.wiki_insert_sign = function(){
      return wiki_insert_sign(this)
    }

    o.wiki_help = function() {
    	return wiki_help();
    }

    o.wiki_save = function()
    {
    	return wiki_save();
    }
    wiki_init();
}

function wiki_init()
{
	services_osvcgetrest("R_WIKI", ['ubuntu'],"", function(jd) {
      if (jd.data === undefined) {
      	$('#wiki_messages').html("No response...");
        return;
      }
      var result=jd.data;
      for(i=0;i<5;i++)
      {
      	var line = "<tr><td>" + result[i].saved_on + "</td><td>"+ result[i].author +"</td></tr>";
      	$("#wiki_table_last_changes").append(line);
      }
      //$('#wiki_messages').html(jd.info);
    });
}

function wiki_help()
{
	toggle("wiki_syntax");
}

function wiki_save()
{
	var value = $('#wiki_tab').val();
	services_osvcpostrest("R_WIKI", ['ubuntu'], "", {"body": value}, function(jd) {
      if (jd.data === undefined) {
      	$('#wiki_messages').html("No response...");
        return
      }
      $('#wiki_messages').html(jd.info);
    },function() {});
}

function wiki_insert_sign()
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
  $("#wiki_tab").insertAtCaret("*" + ds + ", matthieu debray*");
}