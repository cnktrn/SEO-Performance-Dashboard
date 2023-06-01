import React, {useState} from "react";
import {useHistory} from "react-router-dom";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState();

    const history = useHistory();

    const handleSubmit = async (e) => {
        e.preventDefault();

        console.log(username, password)

        const response = await fetch(
            "http://localhost:5555/users/login",
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password})
            }
        )

        const jsonResponse = await response.json();

        if (response.ok) {
            window.localStorage.setItem("token", jsonResponse.token);
            //history.push("/dashboards");
        } else {
            console.log("Something went wrong");
            console.log(jsonResponse);
            setErrorMessage(jsonResponse.message);
        }

    }

    return (
        <div>
            <h2>Login</h2>
            <form onSubmit={e => handleSubmit(e)}>
                <div>
                    Username:
                    <input
                        value={username}
                        type={"text"}
                        onChange={e => setUsername(e.target.value)}
                    />
                </div>
                <div>
                    Password:
                    <input
                        value={password}
                        type={"password"}
                        onChange={e => setPassword(e.target.value)}
                    />
                </div>
                {
                    errorMessage &&
                    <div>{errorMessage}</div>
                }
                <button>Login</button>
            </form>
        </div>
    )
}

export default Login;
