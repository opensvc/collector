data = {
 'opensvc': {
   'title': 'OpenSVC',
   'licences': [
     {
       'prj_name': 'OpenSVC - Agent',
       'prj_www': 'http://www.opensvc.com',
       'link': 'http://www.opensvc.com',
     },
     {
       'prj_name': 'OpenSVC - Collector',
       'prj_www': 'http://www.opensvc.com',
       'link': 'http://www.opensvc.com/init/static/eval/evaluation_agreement.txt',
     },
     {
       'prj_name': 'OpenSVC - Collector',
       'prj_www': 'http://www.opensvc.com',
       'link_type': 'privacy policy',
       'link': 'http://www.opensvc.com/init/static/views/privacypolicy.html',
     },
   ],
 },
 'javascript': {
   'title': 'Javascript',
   'licences': [
     {
       'prj_name': 'Ace',
       'prj_www': 'https://ace.c9.io',
       'link': 'https://github.com/ajaxorg/ace/blob/master/LICENSE',
     },
     {
       'prj_name': "Chai Assertion Library",
       'prj_www': 'http://chaijs.com',
       'link': 'https://github.com/chaijs/chai/blob/master/LICENSE',
     },
     {
       'prj_name': 'Highlight.js',
       'prj_www': 'https://highlightjs.org/',
       'link': 'https://github.com/isagalaev/highlight.js/blob/master/LICENSE',
     },
     {
       'prj_name': "ii18next",
       'prj_www': 'http://i18next.com',
       'link': 'https://github.com/i18next/i18next/blob/master/LICENSE',
     },
     {
       'prj_name': "JQuery",
       'prj_www': 'https://jquery.com/',
       'link': 'https://js.foundation/pdf/ip-policy.pdf',
     },
     {
       'prj_name': 'JS-YAML',
       'prj_www': 'http://nodeca.github.io/js-yaml/',
       'link': 'https://github.com/nodeca/js-yaml/blob/master/LICENSE',
     },
     {
       'prj_name': 'reconnecting-websocket.js',
       'prj_www': 'https://github.com/joewalnes/reconnecting-websocket',
       'link': 'https://github.com/joewalnes/reconnecting-websocket/blob/master/LICENSE.txt',
     },
     {
       'prj_name': 'RequireJS',
       'prj_www': 'http://requirejs.org/',
       'link': 'https://github.com/requirejs/requirejs/blob/master/LICENSE',
     },
     {
       'prj_name': 'jQuery timepicker addon',
       'prj_www': 'http://trentrichardson.com/',
       'link': 'http://trentrichardson.com/Impromptu/MIT-LICENSE.txt',
     },
     {
       'prj_name': 'Tooltipster',
       'prj_www': 'http://iamceege.github.io/tooltipster/',
       'link': 'https://opensource.org/licenses/MIT',
     },
     {
       'prj_name': 'jstree',
       'prj_www': 'https://www.jstree.com/',
       'link': 'https://raw.githubusercontent.com/vakata/jstree/master/LICENSE-MIT',
     },
     {
       'prj_name': 'Moment.js',
       'prj_www': 'http://momentjs.com/',
       'link': 'https://github.com/moment/moment/blob/develop/LICENSE',
     },
     {
       'prj_name': 'Moment Timezone',
       'prj_www': 'http://momentjs.com/timezone/',
       'link': 'https://github.com/moment/moment-timezone/blob/develop/LICENSE',
     },
     {
       'prj_name': 'vis.js',
       'prj_www': 'http://visjs.org/',
       'link': 'http://opensource.org/licenses/MIT',
     },
     {
       'prj_name': 'SuperAgent',
       'prj_www': 'http://visionmedia.github.io/superagent/',
       'link': 'https://github.com/visionmedia/superagent/blob/master/LICENSE',
     },
     {
       'prj_name': 'jqPlot',
       'prj_www': 'http://www.jqplot.com/',
       'link': 'https://opensource.org/licenses/MIT',
     },
     {
       'prj_name': 'Mocha',
       'prj_www': 'https://mochajs.org/',
       'link': 'https://github.com/mochajs/mocha/blob/master/LICENSE',
     },
   ],
 },
 'css': {
   'title': 'CSS',
   'licences': [
     {
       'prj_name': "Font Awesome",
       'prj_www': 'http://fontawesome.io',
       'link': 'http://fontawesome.io/license',
     },
   ],
 },
 'web2py': {
   'title': 'Web2py',
   'licences': [
     {
       'prj_name': 'WEB2PY Web Framework',
       'prj_www': 'http://www.web2py.com',
       'link': 'http://www.gnu.org/licenses/lgpl.html',
     },
   ],
 },
}

def licenses():
    d = []
    for section, sdata in data.items():
        d.append(H1(T(sdata['title'])))
        l = []
        for bdata in sdata['licences']:
            _d = LI(
               A(bdata['prj_name'], 
               _href=bdata['prj_www'],
               _class="clickable", 
               _target="_blank_"),
               A(' ('+bdata.get("link_type", "license")+')', 
               _href=bdata['link'], 
               _class="clickable", 
               _target="_blank_")
            )
            l.append(_d)
        d.append(P(l))
    return dict(table=DIV(d, _class="licenses"))

def licenses_load():
    return licences()["table"]

