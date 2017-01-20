def docker_registry_responsible(id):
    if "Manager" in user_groups():
        return
    q = db.docker_registries_responsibles.registry_id == id
    q &= db.docker_registries_responsibles.group_id.belongs(user_group_ids())
    if db(q).count == 0:
        raise Exception("You are not responsible for this registry")

def docker_registry_responsible(id):
    if "Manager" in user_groups():
        return
    q = db.docker_registries.id == id
    q &= db.docker_registries.id == db.docker_registries_responsibles.registry_id
    q &= db.docker_registries_responsibles.group_id.belongs(user_group_ids())
    registry = db(q).select(db.docker_registries.id).first()
    if registry is None:
        raise Exception("Registry %s not found or you are not responsible" % str(id))

def docker_registry_published(id):
    if "Manager" in user_groups():
        return
    q = db.docker_registries.id == id
    q &= db.docker_registries.id == db.docker_registries_publications.registry_id
    q &= db.docker_registries_publications.group_id.belongs(user_group_ids())
    registry = db(q).select(db.docker_registries.id).first()
    if registry is None:
        raise Exception("Registry %s not found or not published to you" % str(id))

class rest_get_docker_repositories(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List docker repositories in all configured private registries.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories?query=repository contains busy"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories",
          tables=["docker_repositories"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.docker_repositories.id > 0
        q &= docker_repositories_acls_query()
        self.set_q(q)
        return self.prepare_data(**vars)


class rest_get_docker_repository(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List docker repository <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/docker/repositories/<id>",
          tables=["docker_repositories"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.docker_repositories.id == int(id)
        q &= docker_repositories_acls_query()
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_get_docker_registries(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List docker private registries.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/registries"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/registries",
          tables=["docker_registries"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        q = db.docker_registries.id > 0
        self.set_q(q)
        return self.prepare_data(**vars)


class rest_get_docker_registry(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List docker registry <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/registries/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/docker/registries/<id>",
          tables=["docker_registries"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        try:
            q = db.docker_registries.id == int(id)
        except:
            q = db.docker_registries.service == id
        self.set_q(q)
        return self.prepare_data(**vars)


#
# /docker/repositories/<id>/pullers*
#
class rest_get_docker_repository_pullers_apps(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List app allowed to pull the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pullers/apps"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pullers/apps",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_app().handler(s, **vars)
        else:
            q = db.apps.id < 0
            self.set_q(q)
            return self.prepare_data(**vars)


class rest_get_docker_repository_pullers_services(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List services allowed to pull the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pullers/services"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pullers/services",
          tables=["services"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_app_services().handler(s, **vars)
        elif r.repository.startswith("groups/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_group_services().handler(s, **vars)
        elif r.repository.startswith("users/") and r.repository.count("/") > 1:
            q = db.services.id < 0
            self.set_q(q)
            return self.prepare_data(**vars)
        else:
            q = db.auth_group.role == "Everybody"
            q &= db.auth_group.id == db.docker_registries_publications.group_id
            if db(q).count() > 0:
                db.services.id > 0
                self.set_q(q)
                return self.prepare_data(**vars)
            q = db.services.svc_app == db.apps.app
            q &= db.apps_publications.app_id == db.apps.id
            q &= db.apps_publications.group_id == db.docker_registries_publications.group_id
            q &= db.docker_registries_publications.registry_id == r.registry_id
            self.set_q(q)
            return self.prepare_data(**vars)


class rest_get_docker_repository_pullers_groups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups allowed to pull the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pullers/groups"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pullers/groups",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_app_publications().handler(s, **vars)
        elif r.repository.startswith("groups/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_group().handler(s, **vars)
        elif r.repository.startswith("users/"):
            q = db.auth_group.id < 0
            self.set_q(q)
            return self.prepare_data(**vars)
        else:
            q = db.auth_group.id < 0
            self.set_q(q)
            return self.prepare_data(**vars)

class rest_get_docker_repository_pullers_users(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List users allowed to pull from the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pullers/users"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pushers/users",
          tables=["auth_user"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            try:
                q = db.apps.id == int(s)
            except:
                q = db.apps.app == s
            q &= db.apps.id == db.apps_publications.app_id
            q &= db.apps_publications.group_id == db.auth_membership.group_id
            q &= db.auth_user.id == db.auth_membership.user_id
            user_ids = [r.id for r in db(q).select(db.auth_user.id)]

            q = db.auth_user.id.belongs(user_ids)
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            q &= db.auth_group.role == "DockerRegistriesPuller"
            self.set_q(q)
            return self.prepare_data(**vars)
        elif r.repository.startswith("groups/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            try:
                q = db.auth_group.id == int(s)
            except:
                q = db.auth_group.role == s
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            user_ids = [r.id for r in db(q).select(db.auth_user.id)]

            q = db.auth_user.id.belongs(user_ids)
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            q &= db.auth_group.role == "DockerRegistriesPuller"
            self.set_q(q)
            return self.prepare_data(**vars)
        elif r.repository.startswith("users/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            try:
                q = db.auth_user.id == int(s)
            except:
                q = db.auth_user.username == s
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            q &= db.auth_group.role == "DockerRegistriesPuller"
            self.set_q(q)
            return self.prepare_data(**vars)
        else:
            q = db.auth_group.role == "DockerRegistriesPuller"
            q &= db.auth_membership.group_id == db.auth_group.id
            pullers = [row.user_id for row in db(q).select(db.auth_membership.user_id)]

            q = db.docker_registries_publications.registry_id == r.registry_id
            q &= db.docker_registries_publications.group_id == db.auth_membership.group_id
            q &= db.auth_membership.user_id == db.auth_user.id
            q &= db.auth_user.id.belongs(pullers)
            self.set_q(q)
            return self.prepare_data(**vars)


class rest_get_docker_repository_pullers(rest_get_handler):
    def __init__(self):
        desc = [
          "List apps, services and groups allowed to pull the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pullers"
        ]

        rest_get_handler.__init__(
          self,
          path="/docker/repositories/<id>/pullers",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        data = {
          "apps": rest_get_docker_repository_pullers_apps().handler(id, limit=0, props="id,app")["data"],
          "services": rest_get_docker_repository_pullers_services().handler(id, limit=0, props="svc_id,svcname,svc_app")["data"],
          "groups": rest_get_docker_repository_pullers_groups().handler(id, limit=0, props="id,role")["data"],
          "users": rest_get_docker_repository_pullers_users().handler(id, limit=0, props="id,first_name,last_name")["data"],
        }
        return {"data": data}


#
# /docker/repositories/<id>/pushers*
#
class rest_get_docker_repository_pushers_apps(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List app allowed to push to the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pushers/apps"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pushers/apps",
          tables=["apps"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_app().handler(s, **vars)
        else:
            q = db.apps.id < 0
            self.set_q(q)
            return self.prepare_data(**vars)

class rest_get_docker_repository_pushers_groups(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups allowed to push to the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pushers/groups"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pushers/groups",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_app_responsibles().handler(s, **vars)
        elif r.repository.startswith("groups/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            return rest_get_group().handler(s, **vars)
        else:
            q = db.auth_group.id < 0
            self.set_q(q)
            return self.prepare_data(**vars)

class rest_get_docker_repository_pushers_users(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List users allowed to push to the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pushers/users"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/repositories/<id>/pushers/users",
          tables=["auth_user"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        r = get_docker_repository(id)
        if r.repository.startswith("apps/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            try:
                q = db.apps.id == int(s)
            except:
                q = db.apps.app == s
            q &= db.apps.id == db.apps_responsibles.app_id
            q &= db.apps_responsibles.group_id == db.auth_membership.group_id
            q &= db.auth_user.id == db.auth_membership.user_id
            user_ids = [r.id for r in db(q).select(db.auth_user.id)]

            q = db.auth_user.id.belongs(user_ids)
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            q &= db.auth_group.role == "DockerRegistriesPusher"
            self.set_q(q)
            return self.prepare_data(**vars)
        elif r.repository.startswith("groups/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            try:
                q = db.auth_group.id == int(s)
            except:
                q = db.auth_group.role == s
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            user_ids = [r.id for r in db(q).select(db.auth_user.id)]

            q = db.auth_user.id.belongs(user_ids)
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            q &= db.auth_group.role == "DockerRegistriesPusher"
            self.set_q(q)
            return self.prepare_data(**vars)
        elif r.repository.startswith("users/") and r.repository.count("/") > 1:
            s = r.repository.split("/")[1]
            try:
                q = db.auth_user.id == int(s)
            except:
                q = db.auth_user.username == s
            q &= db.auth_user.id == db.auth_membership.user_id
            q &= db.auth_membership.group_id == db.auth_group.id
            q &= db.auth_group.role == "DockerRegistriesPusher"
            self.set_q(q)
            return self.prepare_data(**vars)
        else:
            q = db.auth_group.role == "DockerRegistriesPusher"
            q &= db.auth_membership.group_id == db.auth_group.id
            pushers = [row.user_id for row in db(q).select(db.auth_membership.user_id)]

            q = db.docker_registries_responsibles.registry_id == r.registry_id
            q &= db.docker_registries_responsibles.group_id == db.auth_membership.group_id
            q &= db.auth_membership.user_id == db.auth_user.id
            q &= db.auth_user.id.belongs(pushers)
            self.set_q(q)
            return self.prepare_data(**vars)

class rest_get_docker_repository_pushers(rest_get_handler):
    def __init__(self):
        desc = [
          "List apps, groups and users allowed to push to the docker repository.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/repositories/1/pushers"
        ]

        rest_get_handler.__init__(
          self,
          path="/docker/repositories/<id>/pushers",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        data = {
          "apps": rest_get_docker_repository_pushers_apps().handler(id, limit=0, props="id,app")["data"],
          "groups": rest_get_docker_repository_pushers_groups().handler(id, limit=0, props="id,role")["data"],
          "users": rest_get_docker_repository_pushers_users().handler(id, limit=0, props="id,first_name,last_name")["data"],
        }
        return {"data": data}


class rest_get_docker_registry_publications(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups the docker registry is published to.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/registries/1/publications"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/registries/<id>/publications",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_docker_registry_id(id)
        docker_registry_published(id)
        q = db.docker_registries_publications.registry_id == id
        q &= db.docker_registries_publications.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_docker_registry_publication(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unpublish the docker registry to a group",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/docker/registries/1/publications/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/docker/registries/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, registry_id, group_id, **vars):
        check_privilege("DockerRegistriesManager")
        registry_id = lib_docker_registry_id(registry_id)
        docker_registry_responsible(registry_id)
        q = db.docker_registries_publications.registry_id == registry_id
        q &= db.docker_registries_publications.group_id == group_id

        fmt = "Docker registry %(registry_id)s unpublished to group %(group_id)s"
        d = dict(registry_id=str(registry_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Docker registry %(registry_id)s already unpublished to group %(group_id)s" % d)

        db(q).delete()

        table_modified("docker_registries_publications")
        _log('docker.registry.publication.delete', fmt, d)
        ws_send('docker_registries_publications_change', {'registry_id': registry_id, 'group_id': group_id})
        return dict(info=fmt%d)

class rest_delete_docker_registries_publications(rest_delete_handler):
    def __init__(self):
        desc = [
          "Unpublish the docker registries to groups",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for each deleted docker registry.",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/docker/registries_publications?filters[]="registry_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/docker/registries_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "registry_id" in vars:
            raise Exception("The 'registry_id' key is mandatory")
        registry_id = vars.get("registry_id")
        del(vars["registry_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_docker_registry_publication().handler(registry_id, group_id, **vars)

class rest_post_docker_registry_publication(rest_post_handler):
    def __init__(self):
        desc = [
          "Publish the docker registry to a group",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/docker/registries/1/publications/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/docker/registries/<id>/publications/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, registry_id, group_id, **vars):
        check_privilege("DockerRegistriesManager")
        registry_id = lib_docker_registry_id(registry_id)
        docker_registry_responsible(registry_id)
        group = lib_org_group(group_id)

        fmt = "Docker registry %(registry_id)s published to group %(role)s"
        d = dict(registry_id=str(registry_id), role=str(group.role))

        q = db.docker_registries_publications.registry_id == registry_id
        q &= db.docker_registries_publications.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Docker registry %(registry_id)s already published to group %(role)s" % d)

        db.docker_registries_publications.insert(registry_id=registry_id, group_id=group.id)

        table_modified("docker_registries_publications")
        _log('docker.registry.publication.add', fmt, d)
        ws_send('docker_registries_publications_change', {'registry_id': registry_id, 'group_id': group.id})

        return dict(info=fmt%d)

class rest_post_docker_registries_publications(rest_post_handler):
    def __init__(self):
        desc = [
          "Publish the docker registries to groups",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/docker/registries_publications"
        ]

        rest_post_handler.__init__(
          self,
          path="/docker/registries_publications",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "registry_id" in vars:
            raise Exception("The 'registry_id' key is mandatory")
        registry_id = vars.get("registry_id")
        del(vars["registry_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_docker_registry_publication().handler(registry_id, group_id, **vars)


class rest_get_docker_registry_responsibles(rest_get_table_handler):
    def __init__(self):
        desc = [
          "List groups responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/registries/1/responsibles"
        ]

        rest_get_table_handler.__init__(
          self,
          path="/docker/registries/<id>/responsibles",
          tables=["auth_group"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_docker_registry_id(id)
        docker_registry_published(id)
        q = db.docker_registries_responsibles.registry_id == id
        q &= db.docker_registries_responsibles.group_id == db.auth_group.id
        self.set_q(q)
        data = self.prepare_data(**vars)
        return data

class rest_delete_docker_registry_responsible(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove a form responsible group",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/docker/registries/1/responsibles/2"
        ]

        rest_delete_handler.__init__(
          self,
          path="/docker/registries/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, registry_id, group_id, **vars):
        check_privilege("DockerRegistriesManager")
        registry_id = lib_docker_registry_id(registry_id)
        docker_registry_responsible(registry_id)
        q = db.docker_registries_responsibles.registry_id == registry_id
        q &= db.docker_registries_responsibles.group_id == group_id

        fmt = "Docker registry %(registry_id)s responsibility to group %(group_id)s removed"
        d = dict(registry_id=str(registry_id), group_id=str(group_id))

        row = db(q).select().first()
        if row is None:
            return dict(info="Docker registry %(registry_id)s responsibility to group %(group_id)s already removed" % d)

        db(q).delete()

        table_modified("docker_registries_responsibles")
        _log('docker.registry.responsible.delete', fmt, d)
        ws_send('docker_registries_responsibles_change', {'registry_id': registry_id, 'group_id': group_id})

        return dict(info=fmt%d)

class rest_delete_docker_registries_responsibles(rest_delete_handler):
    def __init__(self):
        desc = [
          "Remove responsible groups from the docker registries",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          """# curl -u %(email)s -X DELETE -o- https://%(collector)s/init/rest/api/docker/registries_responsibles?filters[]="registry_id 1" """
        ]

        rest_delete_handler.__init__(
          self,
          path="/docker/registries_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "registry_id" in vars:
            raise Exception("The 'registry_id' key is mandatory")
        registry_id = vars.get("registry_id")
        del(vars["registry_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_delete_docker_registry_responsible().handler(registry_id, group_id, **vars)

class rest_post_docker_registry_responsible(rest_post_handler):
    def __init__(self):
        desc = [
          "Add a form responsible group",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s -X POST -o- https://%(collector)s/init/rest/api/docker/registries/1/responsibles/2"
        ]

        rest_post_handler.__init__(
          self,
          path="/docker/registries/<id>/responsibles/<group>",
          desc=desc,
          examples=examples,
        )

    def handler(self, registry_id, group_id, **vars):
        check_privilege("DockerRegistriesManager")
        registry_id = lib_docker_registry_id(registry_id)
        docker_registry_responsible(registry_id)
        group = lib_org_group(group_id)

        fmt = "Docker registry %(registry_id)s responsibility to group %(role)s added"
        d = dict(registry_id=str(registry_id), role=str(group.role))

        q = db.docker_registries_responsibles.registry_id == registry_id
        q &= db.docker_registries_responsibles.group_id == group.id
        row = db(q).select().first()
        if row is not None:
            return dict(info="Docker registry %(registry_id)s responsibility to group %(role)s already added" % d)

        db.docker_registries_responsibles.insert(registry_id=registry_id, group_id=group.id)

        table_modified("docker_registries_responsibles")
        _log('docker.registry.responsible.add', fmt, d)
        ws_send('docker_registries_responsibles_change', {'registry_id': registry_id, 'group_id': group.id})

        return dict(info=fmt%d)

class rest_post_docker_registries_responsibles(rest_post_handler):
    def __init__(self):
        desc = [
          "Add responsible groups to docker registry",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
        ]
        examples = [
          "# curl -u %(email)s --header 'Content-Type: application/json' -d @/tmp/data.json -X POST -o- https://%(collector)s/init/rest/api/docker/registries_responsibles"
        ]

        rest_post_handler.__init__(
          self,
          path="/docker/registries_responsibles",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if not "registry_id" in vars:
            raise Exception("The 'registry_id' key is mandatory")
        registry_id = vars.get("registry_id")
        del(vars["registry_id"])

        if not "group_id" in vars:
            raise Exception("The 'group_id' key is mandatory")
        group_id = vars.get("group_id")
        del(vars["group_id"])

        return rest_post_docker_registry_responsible().handler(registry_id, group_id, **vars)

#
class rest_get_docker_registry_am_i_responsible(rest_get_handler):
    def __init__(self):
        desc = [
          "- return true if the requester is responsible for this docker registry.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/registries/1/am_i_responsible",
        ]
        rest_get_handler.__init__(
          self,
          path="/docker/registries/<id>/am_i_responsible",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        id = lib_docker_registry_id(id)
        try:
            docker_registry_responsible(id)
            return dict(data=True)
        except:
            return dict(data=False)


class rest_post_docker_registries(rest_post_handler):
    def __init__(self):
        desc = [
          "Declare a new docker registry.",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry to update an existing registry.",
          "The user primary group is set as publication and responsible.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d service="registry2" -d url="10.0.0.1:5000" https://%(collector)s/init/rest/api/docker/registries""",
        ]
        rest_post_handler.__init__(
          self,
          path="/docker/registries",
          tables=["docker_registries"],
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            id = vars["id"]
            del(vars["id"])
            return rest_post_docker_registry(id, **vars)

        check_privilege("DockerRegistriesManager")
        if len(vars) == 0 or "service" not in vars:
            raise Exception("'service' is mandatory in post data")
        q = db.docker_registries.id > 0
        for v in vars:
            q &= db.docker_registries[v] == vars[v]
        row = db(q).select().first()
        if row is not None:
            return rest_post_docker_registry().handler(row.id, **vars)
        check_quota_docker_registries()
        response = db.docker_registries.validate_and_insert(**vars)
        raise_on_error(response)
        table_modified("docker_registries")
        ws_send('docker_registries_change')
        row = db(q).select().first()

        db.docker_registries_responsibles.insert(registry_id=row.id, group_id=user_default_group_id())
        table_modified("docker_registries_responsibles")
        ws_send('docker_registries_responsibles_change')
        db.docker_registries_publications.insert(registry_id=row.id, group_id=user_default_group_id())
        table_modified("docker_registries_publications")
        ws_send('docker_registries_publications_change')

        _log('docker.registries.create',
             'registry %(s)s created. data %(data)s',
             dict(s=row.service, data=beautify_data(vars)),
            )
        return rest_get_docker_registry().handler(row.id)

#
class rest_post_docker_registry(rest_post_handler):
    def __init__(self):
        desc = [
          "Change a docker registry properties.",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d insecure="T" https://%(collector)s/init/rest/api/docker/registries/1""",
        ]
        rest_post_handler.__init__(
          self,
          path="/docker/registries/<id>",
          tables=["docker_registries"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("DockerRegistriesManager")
        id = lib_docker_registry_id(id)
        docker_registry_responsible(id)
        q = db.docker_registries.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("registry %s does not exist" % str(id))
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        table_modified("docker_registries")
        fmt = 'registry %(s)s changed: %(data)s'
        d = dict(s=row.service, data=beautify_change(row, vars))
        _log('docker.registries.change', fmt, d)
        ws_send('docker_registries_change', {'id': row.id})
        ret = rest_get_docker_registry().handler(row.id)
        ret["info"] = fmt % d
        return ret

#
class rest_post_docker_repository(rest_post_handler):
    def __init__(self):
        desc = [
          "Change a docker repository properties.",
          "The user must be in the DockerRegistriesPusher privilege group.",
          "The user must be responsible for the docker repository.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
          "The id, repository, created and updated fields are not updateable.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X POST -d insecure="T" https://%(collector)s/init/rest/api/docker/repositories/1""",
        ]
        rest_post_handler.__init__(
          self,
          path="/docker/repositories/<id>",
          tables=["docker_repositories"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("DockerRegistriesPusher")
        id = lib_docker_repository_id(id)
        q = db.docker_repositories.id == id
        row = db(q).select().first()
        if row is None:
            raise Exception("repository '%s' does not exist" % str(id))
        q &= docker_repositories_acls_query(action="push")
        row = db(q).select().first()
        if row is None:
            raise Exception("you not allowed to modify repository '%s'" % str(id))
        if "id" in vars:
            del(vars["id"])
        if "repository" in vars:
            del(vars["repository"])
        if "created" in vars:
            del(vars["created"])
        if "updated" in vars:
            del(vars["updated"])
        response = db(q).validate_and_update(**vars)
        raise_on_error(response)
        table_modified("docker_repositories")
        fmt = 'repository %(s)s changed: %(data)s'
        d = dict(s=row.repository, data=beautify_change(row, vars))
        _log('docker.repositories.change', fmt, d)
        ws_send('docker_repositories_change', {'id': row.id})
        ret = rest_get_docker_repository().handler(row.id)
        ret["info"] = fmt % d
        return ret

class rest_delete_docker_registries(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete docker registries and all their repositories and tags from the collector.",
          "This operation does not touch the content of the registry.",
          "Also deletes all responsible and publication group attachments",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/docker/registries""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/docker/registries",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            registry_id = vars["id"]
        elif "service" in vars:
            registry_id = vars["service"]
        else:
            raise Exception("Either the 'id' or 'service' key is mandatory")
        return rest_delete_docker_registry().handler(registry_id)

#
class rest_delete_docker_registry(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a docker_registry.",
          "Also deletes all responsible and publication group attachments",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be responsible for the docker registry.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/docker/registries/1""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/docker/registries/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("DockerRegistriesManager")
        id = lib_docker_registry_id(id)
        docker_registry_responsible(id)
        q = db.docker_registries.id == id
        row = db(q).select().first()
        if row is None:
            return dict(info="docker registry %s does not exist" % str(id))
        db(q).delete()
        table_modified("docker_registries")
        ws_send('docker_registries_change', {'id': row.id})

        q = db.docker_registries_responsibles.registry_id == row.id
        db(q).delete()
        table_modified("docker_registries_responsibles")
        ws_send('docker_registries_responsibles_change')

        q = db.docker_registries_publications.registry_id == row.id
        db(q).delete()
        table_modified("docker_registries_publications")
        ws_send('docker_registries_publications_change')

        q = db.docker_repositories.registry_id == row.id
        db(q).delete()
        table_modified("docker_repositories")
        ws_send('docker_repositories_change')

        q = db.docker_tags.registry_id == row.id
        db(q).delete()
        table_modified("docker_tags")
        ws_send('docker_tags_change')

        _log('docker.registries.delete',
             'docker registry %(s)s deleted',
             dict(s=row.service),
            )
        return dict(info="docker registry %(s)s deleted" % dict(s=row.service))


class rest_delete_docker_tags(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete docker repository tags from the registry and the collector.",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be in a publication group of the docker registry.",
          "The user have acl allowing push on the repository.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/docker/tags""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/docker/tags",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            tag_id = vars["id"]
        else:
            raise Exception("The 'id' key is mandatory")
        return rest_delete_docker_tag().handler(tag_id)

#
class rest_get_docker_tag(rest_get_line_handler):
    def __init__(self):
        desc = [
          "List docker tag <id> properties.",
        ]
        examples = [
          "# curl -u %(email)s -o- https://%(collector)s/init/rest/api/docker/tags/1"
        ]

        rest_get_line_handler.__init__(
          self,
          path="/docker/tags/<id>",
          tables=["docker_tags"],
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        q = db.docker_tags.id == int(id)
        q &= docker_repositories_acls_query()
        self.set_q(q)
        return self.prepare_data(**vars)

class rest_delete_docker_tag(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a docker repository tag from the registry and the collector.",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be in a responsible group of the docker registry.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/docker/tags/1""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/docker/tags/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("DockerRegistriesManager")

        q = db.docker_tags.id == int(id)
        tag = db(q).select().first()
        if tag is None:
            raise Exception("tag '%s' does not exist" % str(id))

        docker_registry_responsible(tag.registry_id)
        repository = get_docker_repository(tag.repository_id)

        docker_delete_tag(tag.registry_id, repository.id, tag.name)
        ws_send('docker_tags_change')
        return dict(info="docker tag %(s)s deleted" % dict(s=str(id)))


class rest_delete_docker_repositories(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete docker repositories and their tags from the registry and the collector.",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be in a publication group of the docker registry.",
          "The user have acl allowing push on the repository.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/docker/repositories""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/docker/repositories",
          desc=desc,
          examples=examples,
        )

    def handler(self, **vars):
        if "id" in vars:
            repository_id = vars["id"]
        else:
            raise Exception("The 'id' key is mandatory")
        return rest_delete_docker_repository().handler(repository_id)

#
class rest_delete_docker_repository(rest_delete_handler):
    def __init__(self):
        desc = [
          "Delete a docker repository and all its tags from the registry and the collector.",
          "The user must be in the DockerRegistriesManager privilege group.",
          "The user must be in a responsible group of the docker registry.",
          "The action is logged in the collector's log.",
          "A websocket event is sent to announce the change in the table.",
        ]
        examples = [
          """# curl -u %(email)s -o- -X DELETE https://%(collector)s/init/rest/api/docker/repositories/1""",
        ]
        rest_delete_handler.__init__(
          self,
          path="/docker/repositories/<id>",
          desc=desc,
          examples=examples,
        )

    def handler(self, id, **vars):
        check_privilege("DockerRegistriesManager")

        q = db.docker_repositories.id == int(id)
        repository = db(q).select().first()
        if repository is None:
            raise Exception("repository '%s' does not exist" % str(id))

        docker_registry_responsible(repository.registry_id)

        q = db.docker_tags.repository_id == repository.id
        q &= db.docker_tags.registry_id == repository.registry_id
        tags = db(q).select()
        for tag in tags:
            docker_delete_tag(tag.registry_id, tag.repository_id, tag.name)

        docker_delete_repository(repository.id)

        ws_send('docker_repositories_change')
        return dict(info="docker repository %(s)s deleted" % dict(s=str(id)))



