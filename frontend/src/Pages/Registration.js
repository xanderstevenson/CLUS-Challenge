
import { useRef, useState, useEffect } from "react";
import { faCheck, faTimes, faInfoCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useNavigate } from 'react-router-dom';
import { useStateIfMounted } from "use-state-if-mounted";
import axios from 'axios';
import './Registration.css';
import styled from 'styled-components';

// Regular expression use for input validation
const USER_REGEX = /^[A-z][A-z0-9-_]{2,24}$/;
const EMAIL_REGEX = /^[A-Za-z0-9]+[._]?[A-Za-z0-9]+[@]\w+[. ]\w{2,3}$/;

const RegisterRectangle = styled.div`
width: 400px;
height: 460px;
overflow: hidden;
position: relative;
box-shadow: -3px 3px 7px #00000075, 3px 3px 7px #00000075, 3px -3px 7px #00000075, -3px -3px 7px #00000075;
margin: 0px auto;
margin-top: -100px;
text-align: center;
background-attachment: fixed;
padding: 15px;
`;

const Registration = () => {
    const navigate = useNavigate();
    const userRef = useRef();
    const errRef = useRef();

    const [firstname, setFirstname] = useState('');
    const [validFirstname, setValidFirstname] = useState(false);
    const [firstnameFocus, setFirstnameFocus] = useState(false);
    
    const [lastname, setLastname] = useState('');
    const [validLastname, setValidLastname] = useState(false);
    const [lastnameFocus, setLastnameFocus] = useState(false);

    const [email, setEmail] = useState('');
    const [validEmail, setValidEmail] = useState(false);
    const [emailFocus, setEmailFocus] = useState(false);

    const [errMsg, setErrMsg] = useState('');

    const [userid,setUserId] = useStateIfMounted('');
    const [car,setCar] = useStateIfMounted('');

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setValidFirstname(USER_REGEX.test(firstname));
    }, [firstname])

    useEffect(() => {
      setValidLastname(USER_REGEX.test(lastname));
    }, [lastname])

    useEffect(() => {
        setValidEmail(EMAIL_REGEX.test(email));
    }, [email])

    useEffect(() => {
        setErrMsg('');
    }, [firstname, lastname, email])

    // Fetch questions from DB
    const [questions,setQuestions] = useState('')
    useEffect(() => {
        const url = `${process.env.REACT_APP_API_URL}/questions`
        console.log(url)
        axios.get(url)
        .then (response => {
            setQuestions(response.data)
        })
    }, []);

    // Wait for response from the (promise) POST before navigate to the new page
    useEffect( () => {
        if( userid !== '' && car === '' ) {
            const url = `${process.env.REACT_APP_API_URL}/start?userid=${userid}`
            console.log(url)
            axios.put(url)
            .then(response => {
                console.log(response.data)
                setCar(response.data)
            })
            .catch( error => {
                console.log(error.response)
                alert('Cannot assign car to user',userid)
            })
        } else if( car !== '' ) {
            console.log('userid',userid)
            {questions.map((question) => question.filename )}
            navigate("/challenge",{state:{first:firstname,userid:userid,car:car,questions:questions}})
            setFirstname('')
            setLastname('')
            setEmail('')
        }
    }, [userid, car]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        // if button enabled with JS hack
        const v1 = USER_REGEX.test(firstname);
        const v2 = USER_REGEX.test(lastname);
        const v3 = EMAIL_REGEX.test(email);
        if (!v1 || !v2 || !v3) {
            setErrMsg("Invalid Entry");
            return;
        }
        try {
            const user = { 
                "email": email,
                "first": firstname,
                "last": lastname
            }
            const url = `${process.env.REACT_APP_API_URL}/user`
            console.log(url)
            axios.post(url, user)
            .then(response => {
                console.log(response.data)
                setUserId(response.data.id)
            })
            .catch( error => {
                console.log(error.response)
                alert('Cannot register user, user may have already taken the challenge',)
            })
        } catch (err) {
            setErrMsg('Registration Failed')
        }
        errRef.current.focus();
    }

    return (
        <RegisterRectangle className="App">
            <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive">{errMsg}</p>
            <h1>User Registration</h1>
            <form onSubmit={handleSubmit}>
                <label htmlFor="firstname">
                    First Name:
                    <FontAwesomeIcon icon={faCheck} className={validFirstname ? "valid" : "hide"} />
                    <FontAwesomeIcon icon={faTimes} className={validFirstname || !firstname ? "hide" : "invalid"} />
                </label>
                <input
                    type="text"
                    id="firstname"
                    ref={userRef}
                    autoComplete="off"
                    onChange={(e) => setFirstname(e.target.value)}
                    value={firstname}
                    required
                    aria-invalid={validFirstname ? "false" : "true"}
                    aria-describedby="uidnote"
                    onFocus={() => setFirstnameFocus(true)}
                    onBlur={()  => setFirstnameFocus(false)}
                />
                <p id="uidnote" className={firstnameFocus && firstname && !validFirstname ? "instructions" : "offscreen"}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    3 to 25 characters.<br />
                    Must begin with a letter.<br />
                    Letters, numbers, underscores, hyphens allowed.
                </p>

                <label htmlFor="lastname">
                    Last Name:
                    <FontAwesomeIcon icon={faCheck} className={validLastname ? "valid" : "hide"} />
                    <FontAwesomeIcon icon={faTimes} className={validLastname || !lastname ? "hide" : "invalid"} />
                </label>
                <input
                    type="text"
                    id="lastname"
                    ref={userRef}
                    autoComplete="off"
                    onChange={(e) => setLastname(e.target.value)}
                    value={lastname}
                    required
                    aria-invalid={validLastname ? "false" : "true"}
                    aria-describedby="uidnote"
                    onFocus={() => setLastnameFocus(true)}
                    onBlur={()  => setLastnameFocus(false)}
                />
                <p id="uidnote" className={lastnameFocus && lastname && !validLastname ? "instructions" : "offscreen"}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    4 to 24 characters.<br />
                    Must begin with a letter.<br />
                    Letters, numbers, underscores, hyphens allowed.
                </p>

                <label htmlFor="email">
                    Email:
                    <FontAwesomeIcon icon={faCheck} className={validEmail ? "valid" : "hide"} />
                    <FontAwesomeIcon icon={faTimes} className={validEmail || !email ? "hide" : "invalid"} />
                </label>
                <input
                    type="text"
                    id="email"
                    autoComplete="off"
                    onChange={(e) => setEmail(e.target.value)}
                    value={email}
                    required
                    aria-invalid={validEmail ? "false" : "true"}
                    aria-describedby="emailnote"
                    onFocus={() => setEmailFocus(true)}
                    onBlur={() => setEmailFocus(false)}
                />
                <p id="emailnote" className={emailFocus && !validEmail ? "instructions" : "offscreen"}>
                    <FontAwesomeIcon icon={faInfoCircle} />
                    8 to 50 characters.<br />
                    Please enter a valid email address<br />
                </p>
                <button disabled={!validFirstname || !validLastname || !validEmail ? true : false}>Start the challenge</button>
            </form>
        </RegisterRectangle>
    )
}

export default Registration;