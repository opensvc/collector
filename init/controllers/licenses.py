data = {
 'opensvc': {
   'title': 'OpenSVC',
   'licences': [
     {
       'prj_name': 'OpenSVC - Agent',
       'prj_www': 'http://www.opensvc.com',
       'prj_lic': 'http://www.opensvc.com',
     },
     {
       'prj_name': 'OpenSVC - Collector',
       'prj_www': 'http://www.opensvc.com',
       'prj_lic': 'http://www.opensvc.com/init/static/eval/evaluation_agreement.txt',
     },
   ],
 },
 'javascript': {
   'title': 'Javascript',
   'licences': [
     {
       'prj_name': 'Ace',
       'prj_www': 'https://ace.c9.io',
       'prj_lic': 'https://github.com/ajaxorg/ace/blob/master/LICENSE',
     },
     {
       'prj_name': "Chai Assertion Library",
       'prj_www': 'http://chaijs.com',
       'prj_lic': 'https://github.com/chaijs/chai/blob/master/LICENSE',
     },
     {
       'prj_name': 'Highlight.js',
       'prj_www': 'https://highlightjs.org/',
       'prj_lic': 'https://github.com/isagalaev/highlight.js/blob/master/LICENSE',
     },
     {
       'prj_name': "ii18next",
       'prj_www': 'http://i18next.com',
       'prj_lic': 'https://github.com/i18next/i18next/blob/master/LICENSE',
     },
     {
       'prj_name': "JQuery",
       'prj_www': 'https://jquery.com/',
       'prj_lic': 'https://js.foundation/pdf/ip-policy.pdf',
     },
     {
       'prj_name': 'JS-YAML',
       'prj_www': 'http://nodeca.github.io/js-yaml/',
       'prj_lic': 'https://github.com/nodeca/js-yaml/blob/master/LICENSE',
     },
     {
       'prj_name': 'reconnecting-websocket.js',
       'prj_www': 'https://github.com/joewalnes/reconnecting-websocket',
       'prj_lic': 'https://github.com/joewalnes/reconnecting-websocket/blob/master/LICENSE.txt',
     },
     {
       'prj_name': 'RequireJS',
       'prj_www': 'http://requirejs.org/',
       'prj_lic': 'https://github.com/requirejs/requirejs/blob/master/LICENSE',
     },
     {
       'prj_name': 'jQuery timepicker addon',
       'prj_www': 'http://trentrichardson.com/',
       'prj_lic': 'http://trentrichardson.com/Impromptu/MIT-LICENSE.txt',
     },
     {
       'prj_name': 'Tooltipster',
       'prj_www': 'http://iamceege.github.io/tooltipster/',
       'prj_lic': 'https://opensource.org/licenses/MIT',
     },
     {
       'prj_name': 'jstree',
       'prj_www': 'https://www.jstree.com/',
       'prj_lic': 'https://raw.githubusercontent.com/vakata/jstree/master/LICENSE-MIT',
     },
     {
       'prj_name': 'Moment.js',
       'prj_www': 'http://momentjs.com/',
       'prj_lic': 'https://github.com/moment/moment/blob/develop/LICENSE',
     },
     {
       'prj_name': 'Moment Timezone',
       'prj_www': 'http://momentjs.com/timezone/',
       'prj_lic': 'https://github.com/moment/moment-timezone/blob/develop/LICENSE',
     },
     {
       'prj_name': 'vis.js',
       'prj_www': 'http://visjs.org/',
       'prj_lic': 'http://opensource.org/licenses/MIT',
     },
     {
       'prj_name': 'SuperAgent',
       'prj_www': 'http://visionmedia.github.io/superagent/',
       'prj_lic': 'https://github.com/visionmedia/superagent/blob/master/LICENSE',
     },
     {
       'prj_name': 'jqPlot',
       'prj_www': 'http://www.jqplot.com/',
       'prj_lic': 'https://opensource.org/licenses/MIT',
     },
     {
       'prj_name': 'Mocha',
       'prj_www': 'https://mochajs.org/',
       'prj_lic': 'https://github.com/mochajs/mocha/blob/master/LICENSE',
     },
   ],
 },
 'css': {
   'title': 'CSS',
   'licences': [
     {
       'prj_name': "Font Awesome",
       'prj_www': 'http://fontawesome.io',
       'prj_lic': 'http://fontawesome.io/license',
     },
   ],
 },
 'web2py': {
   'title': 'Web2py',
   'licences': [
     {
       'prj_name': 'WEB2PY Web Framework',
       'prj_www': 'http://www.web2py.com',
       'prj_lic': 'http://www.gnu.org/licenses/lgpl.html',
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
               A(' (license)', 
               _href=bdata['prj_lic'], 
               _class="clickable", 
               _target="_blank_")
            )
            l.append(_d)
        d.append(P(l))
    return dict(table=DIV(d, _class="licenses"))

def licenses_load():
    return licences()["table"]

