fanmobi-backend
=========================
Backend RESTful API for FanMobi

## Getting Started
1. Install Python 3.4.3. Python can be installed by downloading the appropriate
    files [here](https://www.python.org/downloads/release/python-343/). Note
    that Python 3.4 includes both `pip` and `venv`, a built-in replacement
    for the `virtualenv` package
2. Create a new python environment using python 3.4.x. First, create a new
    directory where this environment will live, for example, in
    `~/python_envs/fanmobi`. Now create a new environment there:
    `python3.4 -m venv ENV` (where `ENV` is the path you used above)
3. Active the new environment: `source ENV/bin/activate`
4. Set Python 3.4 as default `alias python='~/py3env/bin/python3.4'`
5. Install Python development headers `sudo apt-get install python3-dev`
6. Install the necessary dependencies into this python environment:
    `pip install -r requirements.txt`
7. Run the server: `./restart_clean_dev_server.sh`

Swagger documentation for the api is available at `http://localhost:8000/docs/`
Use username `user` password `password` when prompted for authentication info

## API Notes
Most of the documentation for the API should be accessed via Swagger. Below are
some high level descriptions of the various endpoints that should make
navigating the Swagger docs a little easier

General notes:
* PATCH requests are not implemented - don't try and use these
* PUT requests will update an entire record - if data is not provided, it will
    be treated as null
* Unless a user is an ADMIN, they only have access to their own data

### Login/Logout
All requests (other than these) must be authenticated. Session-based
authentication is used to keep track of the current user. The login endpoint
will create the user if they don't currently exist - this is the currently
supported mechanism for creating new users and artists

####Useful endpoints
Method | Endpoint | Description
------ | -------- | -----
POST | `/api/login/` | login
POST | `/api/logout/` | logout

Permissions: open
### User
This is a lower-level thing used by default in Django - don't use this
endpoint directly

Permissions: ADMIN access only
### Group
A Group is a Role, and a user can belong to one or more groups. Currently, we
are using three groups: FAN, ARTIST, and ADMIN. There shouldn't be a need to
change anything here, but these three groups must be created in the database

Permissions: ADMIN access only
### Genre
Names of music genres. Artists have zero or more music genres associated with
them. **TBD:** Need to decide whether these genres are pre-populated and thus
read-only by non-ADMINs, or if artists should be able to create their own
genres

#### Useful endpoints
Method | Endpoint | Description
------ | -------- | -----
GET | `/api/genre/` | Get all genres

Permissions: ADMIN has full access, authenticated users have read-only

### Image
Images for use with avatars. Images are stored on disk (not in the database).
All Profiles can have an associated avatar (so they are not limited to artists)

Method | Endpoint | Description
------ | -------- | -----
GET | `/api/image/` | Get all images
POST | `/api/image/` | Upload an image (don't use Swagger to test this)
GET | `/api/image/<id>` | Get an image

Permissions: Authenticated has full access

### Profile
Every user of Fanmobi has a Profile. At a minimum, a Profile has an associated
user with a username and belongs to at least one Group (FAN by default). Trying
to access a user profile other than your own will result in a 403 (unless you
are an ADMIN). Once created, **usernames cannot currently be changed**

Profiles are created automatically when a new user tries to login. Note that
the POST endpoint to create a new user is not implemented yet

#### Useful Endpoints
Method | Endpoint | Usage
------ | -------- | -----
GET  | `/api/profile/` | returns all Profiles - ADMIN use only
GET  | `/api/profile/<id>/` | returns a user's profile
PUT  | `/api/profile/<id>/` | update a user's profile (cannot update avatar from Swagger)
GET | `/api/profile/<id>/message/` | returns all unread messages for a user
DELETE | `/api/profile/<profile_id>/message/<message_id>/` | mark a message as read
GET | `/api/profile/<profile_id>/connected/` | get artist connections
PUT | `/api/profile/<profile_id>/connected/<artist_id>/` | connect to an artist
DELETE | `/api/profile/<profile_id>/connected/<artist_id>/` | disconnect from an artist

### Artist
In addition to a Profile, artists have an ArtistProfile containing additional
information. Artists can also create messages for their followers and
update show information

#### Useful Endpoints
Method | Endpoint | Usage
------ | -------- | -----
GET  | `/api/artist/` | returns all Artist profiles (open to any authenticated user)
GET  | `/api/artist/<id>/` | return information for a single artist
PUT  | `/api/artist/<id>/` | update artist information (does not work from Swagger)
GET  | `/api/artist/<id>/show/` | get all shows for an artist
POST  | `/api/artist/<id>/show/` | create a new show
PUT  | `/api/artist/<id>/show/<show_id>/` | update an existing show
DELETE  | `/api/artist/<id>/show/<show_id>/` | delete an existing show
GET  | `/api/artist/<id>/connected/` | get all users connected to this artist
GET  | `/api/artist/<id>/message/` | get all messages from this artist
POST  | `/api/artist/<id>/message/` | create a message from this artist
DELETE  | `/api/artist/<id>/message/<message_id>/` | delete this message
GET  | `/api/artists-in-radius/` | get artists in radius (km) of coordinates (latitude and longitude in decimal degrees)


Like other users, artists are created when a new user tries to login (and specifies
that they are an artist). The POST endpoint to create a new artist is not fully
implemented
