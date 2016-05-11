var assert = chai.assert
var expect = chai.expect
var should = chai.should()
var request = superagent

var original_user_id = null
var impersonate_group_id = null
var everybody_group_id = null
var mocha_user = "mocha@opensvc.com"
var mocha_user_id = null
var mocha_app_id = null
var mocha_users = null

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
				"filters": ["role Impersonate"],
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
				"filters": ["role Everybody"],
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
				"first_name": "mocha",
				"last_name": "mocha"
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
})
describe('Application code management', function() {
	describe('Get mocha user private apps', function () {
		it('Returns 1 app', function(done) {
			request
			.get("/init/rest/api/apps")
			.query({
				"filters": ["app user_"+mocha_user_id+"_app"]
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
				"filters": ["email mocha@opensvc.com"],
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

