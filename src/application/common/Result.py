class Result:
    def __init__(self, code,message,data):
        self.code = code
        self.message = message
        self.data =data

    @staticmethod
    def success(data=None, message="success"):
        return {"code": 200, "message": message, "data": data}

    @staticmethod
    def error(code=500, message="服务器内部错误"):
        return {"code": code, "message": message, "data": None}

    @staticmethod
    def unauthorized(message="未登录或 token 过期"):
        return {"code": 401, "message": message, "data": None}