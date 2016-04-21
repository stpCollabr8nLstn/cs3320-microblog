from init import app

import views, views_auth, api

if __name__ == '__main__':
    app.run(debug=True)
