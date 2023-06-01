import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";

const accessTokenSecret = "577980122d590fe9004fe";

export const generateJWT = (user) => {
    return jwt.sign({ username: user.username }, accessTokenSecret);
}

export const authenticateJWT = (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (authHeader) {
        const token = authHeader.split(' ')[1];
        jwt.verify(token, accessTokenSecret, (err, content) => {
            if (err) {
                return res.sendStatus(403);
            }
            req.username = content.username;
            next();
        });
    } else {
        res.sendStatus(401);
    }
};

export const generateHash = async (password) => {
    return await bcrypt.hash(password, 12);
}

export const comparePassword = async (testString, hash) => {
    return await bcrypt.compare(testString, hash);
}