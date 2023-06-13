import mongoose from "mongoose";

const userSchema = mongoose.Schema({
    username: {
        type: String,
        unique: true
    },
    password: String,
    dashboards: [String]
})

const User = mongoose.model("User", userSchema);

export default User;