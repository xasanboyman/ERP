import jwt from 'jsonwebtoken';

const SECRET_KEY = process.env.SECRET_KEY || 'super-secret-key-that-is-hard-to-guess';

export function authenticate(req, res) {
  try {
    if (req.method === 'OPTIONS') {
      return true;
    }

    const authHeader = req?.headers?.authorization || req?.headers?.Authorization;
    if (!authHeader) {
      res.status(401).json({
        code: 401,
        message: 'Avtorizatsiya talab qilinadi. Iltimos, tizimga kiring.'
      });
      return null;
    }

    let token = String(authHeader).trim();
    if (token.startsWith('Bearer ') || token.startsWith('bearer ')) {
      token = token.slice(7).trim();
    }

    const payload = jwt.verify(token, SECRET_KEY);
    return payload;
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      res.status(401).json({
        code: 401,
        message: 'Sessiya muddati tugadi. Iltimos qaytadan kiring.'
      });
    } else {
      res.status(401).json({
        code: 401,
        message: 'Yaroqsiz token: ' + err.message
      });
    }
    return null;
  }
}
