import uvicorn
from frameworks_and_drivers.web.flask_router import app as flask_app
from frameworks_and_drivers.web.fastapi_router import app as fastapi_app

# flaskを採用する場合
flask_app.run(debug=True, host='0.0.0.0')
# fast_apiを採用する場合
# uvicorn.run(app=fastapi_app, host="0.0.0.0", port=5000)
