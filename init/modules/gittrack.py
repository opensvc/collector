import os
from subprocess import *
import copy
import uuid

class gittrack(object):
    def __init__(self, otype='sysreport'):
        bdir = 'uploads'
        if otype != 'sysreport':
            bdir = 'private'
        self.otype = otype
        here_d = os.path.dirname(__file__)
        self.collect_d = os.path.join(here_d, '..', bdir, self.otype)
        self.cwd = os.getcwd()

    def timeline(self, nodes=[], path=None, begin=None, end=None):
        data = []
        for node in nodes:
            data += self._timeline(node, path=path, begin=begin, end=end)
        return data

    def _timeline(self, data_id, path=None, begin=None, end=None):
        s = self.log(data_id, path=path, begin=begin, end=end)
        data = self.parse_log(s, data_id)
        if self.otype == 'sysreport':
            if len(data) > 1:
                # do not to display the node sysreport initial commit
                data = data[:-1]
        return data

    def parse_log(self, s, data_id):
        data = []
        d0 = {
         'id': '',
         'cid': '',
         'start': '',
         'stat': ''
        }
        d = copy.copy(d0)

        for line in s.split('\n'):
            if line.startswith("commit"):
                if d['start'] != '':
                    data.append(d)
                    d = copy.copy(d0)
                d['cid'] = line.split()[1]
                if self.otype == 'sysreport':
                    d['id'] = uuid.uuid1().hex
                else:
                    d['id'] = d['cid']
            elif self.otype != 'sysreport' and line.startswith("Author:"):
                d['content'] = line
            elif self.otype != 'sysreport' and line.strip().startswith("rollback"):
                d['content'] += "<br>"+line
            elif line.startswith("Date:"):
                l = line.split()
                d['start'] = "T".join(l[1:3])
            elif d['cid'] != '' and d['start'] != '':
                d['stat'] += line+'\n'
        if d['start'] != '':
            data.append(d)

        for i, d in enumerate(data):
            changed = set([])
            for line in d['stat'].split('\n'):
                if "files changed" in line:
                    d['summary'] = line.strip()
                    continue
                if " | " not in line:
                    continue
                fpath = line.split(" | ")[0].strip().strip('"')
                changed.add(fpath)
            data[i]['stat'] = sorted(changed)
            data[i]['group'] = data_id
        return data

    def log(self, data_id=None, path=None, begin=None, end=None):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "log", "-n", "300",
               "--stat=510,500", "--date=iso", "--all"]
        if begin:
            cmd += ['--since='+begin]
        if end:
            cmd += ['--until='+end]
        if path:
            cmd += ['--', path]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def show_data(self, cid, data_id, path=None, begin=None, end=None):
        if begin or end:
            ss = ""
            s = self.diff(data_id, path=path, begin=begin, end=end)
        elif cid:
            ss = self.show_stat(cid, data_id, path=path)
            s = self.show(cid, data_id, path=path)
        else:
            ss = ""
            s = ""
        data = self.parse_show(s)
        data['stat'] = self.parse_show_stat(ss)
        return data

    def diff(self, data_id, path=None, begin=None, end=None):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "diff", '--pretty=format:%ci%n%b']
        if begin:
            cmd += ['master@{%s}'%begin]
        if end:
            cmd += ['master@{%s}'%end]
        if path:
            cmd += ["--", path]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if len(err) > 0 and "only goes back" in err:
            raise Exception(err)
        return out

    def diff_cids(self, data_id, cid1, cid2, filename=None):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "diff", '--pretty=format:%ci%n%b', cid1, cid2]
        if filename:
            cmd += ["--", filename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def show(self, cid, data_id, path=None, numstat=False, patch=True):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "show", '--pretty=format:%ci%n%b', cid]
        if numstat:
            cmd += ['--numstat']
        if patch:
            cmd += ['--patch']
        if path and path != "":
            cmd += ["--", path]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def show_stat(self, cid, data_id, path=None):
        return self.show(cid, data_id, path=path, patch=False, numstat=True)

    def parse_show_stat(self, s):
        data = {}
        if s is None:
            return data
        lines = s.split("\n")
        for line in lines:
            try:
                insertions, deletions, fpath = line.split("\t")
                insertions = int(insertions)
                deletions = int(deletions)
            except:
                continue
            data[fpath] = (insertions, deletions)
        return data

    def parse_show(self, s):
        lines = s.split("\n")
        if len(lines) > 0:
            if 'diff' in lines[0]:
                date = ""
            else:
                date = lines[0]
                lines = lines[1:]
        else:
            date = ''
        d = {}
        block = []
        fpath = ''
        import re
        re1 = re.compile(r".*/cmd/")
        re2 = re.compile(r".*/file/")
        for line in lines:
            if line.startswith("diff "):
                if fpath != "" and len(block) > 0:
                    d[fpath] = '\n'.join(block)
                    block = []
                    fpath = ""
                continue
            if line.startswith("index "):
                continue
            if line.startswith("--- ") or line.startswith("+++ "):
                if "/dev/null" not in line:
                    fpath = re1.sub('cmd/', line)
                    fpath = re2.sub('file/', fpath)
                continue
            block.append(line)
        if fpath != "" and len(block) > 0:
            d[fpath] = '\n'.join(block)
        return {'date': date, 'blocks': d}

    def lstree(self, cid, data_id, path=None):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "ls-tree", "-r", cid]
        if path:
            base_d = os.path.join(git_d, '..')
            path = path.replace("//", "/")
            f_cmd = ["find", base_d, "-path", path]
            p = Popen(f_cmd, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            paths = out.split("\n")
            paths = map(lambda x: x.replace(base_d+"/", ""), paths)
            paths.remove("")
            if len(paths) == 0:
                return ""
            cmd += ["--"] + paths
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def parse_lstree(self, cid, s):
        data = []
        for line in s.split('\n'):
            l = line.split()
            if len(l) < 4:
                continue
            d = {
              "cid": cid,
              "mode": l[0],
              "type": l[1],
              "oid": l[2],
              "fpath": line.split("	")[-1].strip('"'),
            }
            data.append(d)
        return data

    def lstree_data(self, cid, data_id, path=None):
        if cid is None:
            return []
        s = self.lstree(cid, data_id, path=path)
        return self.parse_lstree(cid, s)

    def show_file_unvalidated(self, cid, _uuid, data_id):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "show", _uuid]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return {'oid': _uuid, 'content': out}

    def show_file(self, fpath, cid, _uuid, data_id):
        git_d = os.path.join(self.collect_d, data_id, ".git")
        cmd = ["git", "--git-dir="+git_d, "ls-tree", cid, fpath]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        try:
            validated_fpath = out[out.index("\t")+1:]
        except:
            validated_fpath = fpath

        cmd = ["git", "--git-dir="+git_d, "show", _uuid]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return {'fpath': validated_fpath, 'content': out}

    def init_repo(self, data_id, author=None):
        import config
        git_d = os.path.join(self.collect_d, data_id)
        os.system("mkdir -p " + git_d)
        git_d += "/.git"
        if hasattr(config, "email_from"):
            email = config.email_from
        else:
            email = "nobody@localhost.localdomain"
        if author:
            author = "--author='%s'" % author.encode("utf-8")
        else:
            author = ""
        cmd = ["git", "--git-dir="+git_d, "init"]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        os.system("git --git-dir=%s config user.email %s" % (git_d, email))
        os.system("git --git-dir=%s config user.name collector" % git_d)
        os.system("cd %(git_d)s/.. && (rm -f .git/index.lock ; git add . ; git commit -m'initial commit' %(author)s -a)" % dict(
            git_d=git_d,
            author=author,
        ))

    def commit(self, data_id, content, author=None):
        git_d = os.path.join(self.collect_d, data_id)
        if not os.path.exists(git_d):
            self.init_repo(data_id, author=author)
        with open(git_d+"/"+self.otype, "w") as text_file:
            text_file.write(content)
        if author:
            author = "--author='%s'" % author.encode("utf-8")
        else:
            author = ""
        cf = "cd %(git_d)s && (git add %(otype)s; git commit -m'change' %(author)s -a)" % dict(
            git_d=git_d,
            otype=self.otype,
            author=author,
        )
        os.system(cf)
        return 0

    def rollback(self, data_id, cid, author=None):
        git_d = os.path.join(self.collect_d, data_id)
        date = self.show_data(cid, data_id)["date"]
        if author:
            author = "--author='%s'" % author.encode("utf-8")
        cmd = "cd %(git_d)s && (git checkout %(cid)s %(otype)s; git commit -m'rollback to %(date)s' %(author)s -a)" % dict(
            git_d=git_d,
            cid=cid,
            otype=self.otype,
            author=author,
            date=date,
        )
        os.system(cmd)
        return 0

if __name__ == "__main__":
    o = gittrack()
    #print(o.timeline(["clementine"]))
    print(o.lstree_data('f8f48a59d61501e290cb521641ff27bd747252cb', 'clementine'))
