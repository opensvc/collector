var assert = chai.assert
var expect = chai.expect
var should = chai.should()
var request = superagent

var original_user_id = null
var impersonate_group_id = null
var everybody_group_id = null
var mocha_user = "mocha@opensvc.com"
var mocha_user_id = null
var mocha_group_id = null
var mocha_app_id = null
var mocha_users = null

var api = null
var priv_groups_h = {}

describe('API description', function() {
	it('Returns the api description', function(done) {
		request
		.get("/init/rest/api")
		.end(function(err, res){
			res.status.should.be.equal(200)
			res.body.should.have.property("data")
			api = res.body.data
			console.log(api)
			done()
		})
	})
	var l = ["GET", "POST", "DELETE", "PUT"]
	l.forEach(function(k) {
		it('Contains a key '+k, function(done) {
			api.should.have.property(k)
			done()
		})
	})
})
describe('Scheduler tasks', function() {
	var tasks = null
	var removed_tasks = [
		"task_refresh_b_disk_app",
		"task_refresh_b_apps"
	]
	var target_tasks = [
		"task_purge_checks",
		"task_unfinished_actions",
		"task_feed_monitor",
		"task_purge_static",
		"task_alerts_hourly",
		"task_alerts_daily",
		"task_metrics",
		"task_stats",
		"task_refresh_obsolescence",
		"task_dash_comp",
		"task_dash_min",
		"task_dash_hourly",
		"task_dash_daily",
		"task_purge_feed"
	]

	it('Returns the scheduler endlessly repeating tasks', function(done) {
		request
		.get("/init/rest/api/scheduler/tasks")
		.query({
			"props": "function_name",
			"filters": "repeats 0",
			"meta": "0",
			"limit": "0"
		})
		.end(function(err, res){
			res.status.should.be.equal(200)
			res.body.data.should.be.a("array")
			res.body.data.length.should.greaterThan(0)
			res.body.data[0].should.have.property("function_name")
			tasks = []
			for (var i=0; i<res.body.data.length; i++) {
				tasks.push(res.body.data[i].function_name)
			}
			done()
		})
	})
	target_tasks.forEach(function(s) {
		it('Should contain '+s, function(done) {
			tasks.should.contain(s)
			done()
		})
	})
	removed_tasks.forEach(function(s) {
		it('Should not contain '+s, function(done) {
			tasks.should.not.contain(s)
			done()
		})
	})
})
describe('Privilege Groups', function() {
	var priv_groups = null
	var target_priv_groups = [
		"AppManager",
		"CheckExec",
		"CheckManager",
		"CheckRefresh",
		"CompExec",
		"CompManager",
		"DnsManager",
		"FormsManager",
		"Manager",
		"NetworkManager",
		"NodeExec",
		"NodeManager",
		"ObsManager",
		"ProvisioningManager",
		"ReportsManager",
		"SafeUploader",
		"StorageExec",
		"StorageManager",
		"TagManager",
		"UserManager"
	]

	it('Returns the privilege groups list', function(done) {
		request
		.get("/init/rest/api/groups")
		.query({
			"props": "id,role",
			"filters": "privilege T",
			"meta": "0",
			"limit": "0"
		})
		.end(function(err, res){
			res.status.should.be.equal(200)
			res.body.data.should.be.a("array")
			res.body.data.length.should.greaterThan(0)
			res.body.data[0].should.have.property("id")
			res.body.data[0].should.have.property("role")
			priv_groups = []
			for (var i=0; i<res.body.data.length; i++) {
				priv_groups.push(res.body.data[i].role)
				priv_groups_h[res.body.data[i].role] = res.body.data[i].id
			}
			done()
		})
	})
	target_priv_groups.forEach(function(g) {
		it('Should contain '+g, function(done) {
			priv_groups.should.contain(g)
			done()
		})
	})
})
describe('Test scenario', function() {
	describe('Create a new user and impersonate', function() {
		describe('Get original user id', function () {
			it('Returns an array of 1 user', function(done) {
				request
				.get("/init/rest/api/users/self")
				.query({
					"props": "id",
					"meta": "0",
					"limit": "0"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.equal(1)
					res.body.data[0].should.have.property("id")
					original_user_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Get the Impersonate group id', function () {
			it('Returns an array of 1 group', function(done) {
				request
				.get("/init/rest/api/groups")
				.query({
					"filters": "role Impersonate",
					"props": "id",
					"meta": "0",
					"limit": "0"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.equal(1)
					res.body.data[0].should.have.property("id")
					impersonate_group_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Get the Everybody group id', function () {
			it('Returns an array of 1 group', function(done) {
				request
				.get("/init/rest/api/groups")
				.query({
					"filters": "role Everybody",
					"props": "id",
					"meta": "0",
					"limit": "0"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.equal(1)
					res.body.data[0].should.have.property("id")
					everybody_group_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Create the mocha user', function () {
			it('Returns a user structure in data[0]', function(done) {
				request
				.post("/init/rest/api/users")
				.send({
					"email": mocha_user,
					"quota_app": 1,
					"first_name": "mocha"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.be.greaterThan(0)
					res.body.data[0].should.have.property("id")
					mocha_user_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Get the mocha user private group id', function () {
			it('Returns an array of 1 group', function(done) {
				request
				.get("/init/rest/api/users/"+mocha_user_id+"/groups")
				.query({
					"props": "id,role",
					"meta": "0",
					"limit": "0"
				})
				.query({"filters[]": "privilege F"})
				.query({"filters[]": "role !Everybody"})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.equal(1)
					res.body.data[0].should.have.property("id")
					mocha_group_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Set the ProvisioningManager privilege to mocha user', function () {
			it('Returns no error and attached in info', function(done) {
				request
				.post("/init/rest/api/users/"+mocha_user_id+"/groups/"+priv_groups_h["ProvisioningManager"])
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/attached/)
					done()
				})
			})
		})
		describe('Set the FormsManager privilege to mocha user', function () {
			it('Returns no error and attached in info', function(done) {
				request
				.post("/init/rest/api/users/"+mocha_user_id+"/groups/"+priv_groups_h["FormsManager"])
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/attached/)
					done()
				})
			})
		})
		describe('Set the Impersonate privilege to mocha user', function () {
			it('Returns no error and attached in info', function(done) {
				request
				.post("/init/rest/api/users/"+mocha_user_id+"/groups/"+impersonate_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/attached/)
					done()
				})
			})
		})
		describe('Impersonate the mocha user', function () {
			it('Returns no error', function(done) {
				request
				.post("/init/default/user/impersonate")
				.type("form")
				.send({"user_id": mocha_user_id})
				.end(function(err, res){
					res.status.should.be.equal(200)
					done()
				})
			})
		})
	})
	describe('Non Manager user management', function() {
		describe('Set the mocha user app quota', function () {
			it('Should fail because not a QuotaManager member', function(done) {
				request
				.post("/init/rest/api/users/"+mocha_user_id)
				.send({
					"quota_app": 2
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.have.property("error")
					res.body.should.not.have.property("info")
					res.body.error.should.match(/No fields to update/)
					done()
				})
			})
		})
		describe('Try to get the Manager privilege', function () {
			it('Should fail because not a Manager member', function(done) {
				request
				.post("/init/rest/api/users/"+mocha_user_id+"/groups/"+priv_groups_h["Manager"])
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.have.property("error")
					res.body.should.not.have.property("info")
					res.body.error.should.match(/not exist/)
					done()
				})
			})
		})
	})
	describe('Forms management', function() {
		var form_id = null
		describe('Create a form', function () {
			it('Returns the created form structure in data[0]', function(done) {
				request
				.post("/init/rest/api/forms")
				.send({
					"form_name": "mocha form"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.equal(1)
					res.body.data[0].should.have.property("form_name")
					res.body.data[0].form_name.should.be.equal("mocha form")
					res.body.data[0].should.have.property("id")
					form_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Get form publications', function () {
			it('Should return only the mocha private group', function(done) {
				request
				.get("/init/rest/api/forms/"+form_id+"/publications")
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.length.should.equal(1)
					res.body.data[0].id.should.equal(mocha_group_id)
					done()
				})
			})
		})
		describe('Get form responsibles', function () {
			it('Should return only the mocha private group', function(done) {
				request
				.get("/init/rest/api/forms/"+form_id+"/responsibles")
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.length.should.equal(1)
					res.body.data[0].id.should.equal(mocha_group_id)
					done()
				})
			})
		})
		describe('Publish the form to Everybody', function () {
			it('Returns no error and published in info', function(done) {
				request
				.post("/init/rest/api/forms/"+form_id+"/publications/"+everybody_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/published/)
					done()
				})
			})
		})
		describe('Unpublish the form to Everybody', function () {
			it('Returns no error and unpublished in info', function(done) {
				request
				.del("/init/rest/api/forms/"+form_id+"/publications/"+everybody_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/unpublished/)
					done()
				})
			})
		})
		describe('Give responsibility of the form to Everybody', function () {
			it('Returns no error and added in info', function(done) {
				request
				.post("/init/rest/api/forms/"+form_id+"/responsibles/"+everybody_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/added/)
					done()
				})
			})
		})
		describe('Revoke responsibility of the form to Everybody', function () {
			it('Returns no error and removed in info', function(done) {
				request
				.del("/init/rest/api/forms/"+form_id+"/responsibles/"+everybody_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/removed/)
					done()
				})
			})
		})
		describe('Delete the form', function () {
			it('Returns no error and deleted in info', function(done) {
				request
				.del("/init/rest/api/forms/"+form_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/deleted/)
					done()
				})
			})
		})
	})
	describe('Application code management', function() {
		describe('Get mocha user private apps', function () {
			it('Returns 1 app', function(done) {
				request
				.get("/init/rest/api/apps")
				.query({
					"filters": "app user_"+mocha_user_id+"_app"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.length.should.equal(1)
					mocha_app_id = res.body.data[0].id
					done()
				})
			})
		})
		describe('Rename the user private app', function () {
			it('Returns the modified app structure in data[0]', function(done) {
				request
				.post("/init/rest/api/apps/"+mocha_app_id)
				.send({
					"app": "MOCHA"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					res.body.data.length.should.equal(1)
					res.body.data[0].should.have.property("app")
					res.body.data[0].app.should.be.equal("MOCHA")
					done()
				})
			})
		})
		describe('Publish the private app to Impersonate', function () {
			it('Should fail because Impersonate is a privilege group', function(done) {
				request
				.post("/init/rest/api/apps/"+mocha_app_id+"/publications/"+impersonate_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.have.property("error")
					res.body.should.not.have.property("info")
					res.body.error.should.match(/not allowed on privilege group/)
					done()
				})
			})
		})
		describe('Publish the private app to Everybody', function () {
			it('Returns the modified app structure in data[0]', function(done) {
				request
				.post("/init/rest/api/apps/"+mocha_app_id+"/publications/"+everybody_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/published/)
					done()
				})
			})
		})
		describe('Give responsability of the private app to Impersonate', function () {
			it('Should fail because Impersonate is a privilege group', function(done) {
				request
				.post("/init/rest/api/apps/"+mocha_app_id+"/responsibles/"+impersonate_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.have.property("error")
					res.body.should.not.have.property("info")
					res.body.error.should.match(/not allowed on privilege group/)
					done()
				})
			})
		})
		describe('Give responsability of the private app to Everybody', function () {
			it('Returns the modified app structure in data[0]', function(done) {
				request
				.post("/init/rest/api/apps/"+mocha_app_id+"/responsibles/"+everybody_group_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					done()
				})
			})
		})
		describe('Create another app', function () {
			it('Should fail because of exceeded app quota', function(done) {
				request
				.post("/init/rest/api/apps")
				.send({
					"app": "MOCHA2"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.have.property("error")
					res.body.should.not.have.property("info")
					res.body.error.should.match(/quota exceeded/)
					done()
				})
			})
		})
	})
	describe('Impersonate back to the original user and cleanup', function() {
		describe('Impersonate back to the original user', function () {
			it('Returns no error', function(done) {
				request
				.post("/init/default/user/impersonate")
				.type("form")
				.send({"user_id": original_user_id})
				.end(function(err, res){
					res.status.should.be.equal(200)
					done()
				})
			})
		})
		describe('Delete the mocha private app', function () {
			it('Returns no error and deleted in info', function(done) {
				request
				.del("/init/rest/api/apps/"+mocha_app_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/deleted/)
					done()
				})
			})
		})
		describe('Delete the mocha user', function () {
			it('Returns no error and deleted in info', function(done) {
				request
				.del("/init/rest/api/users/"+mocha_user_id)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.should.not.have.property("error")
					res.body.should.have.property("info")
					res.body.info.should.match(/deleted/)
					done()
				})
			})
		})
		describe('List left-over mocha users', function () {
			it('Returns an array of users', function(done) {
				request
				.get("/init/rest/api/users")
				.query({
					"filters": "email mocha@opensvc.com",
					"props": "id",
					"meta": "0",
					"limit": "0"
				})
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.data.should.be.a("array")
					mocha_users = res.body.data
					done()
				})
			})
		})
		describe('Delete left-over mocha users', function () {
			it('Returns no error', function(done) {
				request
				.del("/init/rest/api/users")
				.send(mocha_users)
				.end(function(err, res){
					res.status.should.be.equal(200)
					res.body.error.length.should.equal(0)
					done()
				})
			})
		})
	})
})

