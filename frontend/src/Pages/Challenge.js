import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';

// More Material UI examples
// https://react.school/material-ui/templates
import {
  makeStyles,
  createTheme,
  ThemeProvider
} from "@material-ui/core/styles";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Container from "@material-ui/core/Container";
import {  blue, pink } from "@material-ui/core/colors";

const useStyles = makeStyles((theme) => ({
  margin: {
    "& > *": {
      margin: theme.spacing(1)
    }
  },
  spacer: {
    marginBottom: theme.spacing(10)
  }
}));

const defaultTheme = createTheme({
  palette: {
    primary: blue,
    secondary: pink
  }
});

const StyledImage = styled.img`
    width: 960px;
    height: 540px;
    object-fit: full-width;
`;

const AnimatedChoiceButtons = styled.button`
    width: 75px;
    height:50px;
    padding: 5px 5px;
    font-size: 28px;
    text-align: center;
    line-height: 25px;
    color: rgba(255,255,255,0.9);
    border-radius: 50px;
    background: linear-gradient(-45deg, #FFA63D, #FF3D77, #338AFF, #3CF0C5);
    background-size: 600%;
    animation: anime 16s linear infinite;
    box-shadow: 1px 1px 6px rgb(59, 0, 59), -1px 1px 6px rgb(59, 0, 59);
    margin: 10px;
    opacity: 0.9;

    @keyframes anime {
      0% {
        background-position: 0% 50%
        }
      50%
        {
        background-position: 100% 50%
        }
      100%
        {
      background-position: 0% 50%
        }
      }

      &:hover {
        opacity: 0.9;
        transform: scale(0.98);
      }
`;

const Challenge = () => {
    const classes = useStyles();
    const navigate = useNavigate();
    const [answer,setYourAnswer] = useState();
    const [qindex,setQIndex] = useState(0)

    // Information passing from registration page
    let location = useLocation()
    const firstname = location.state.first
    const userid    = location.state.userid
    const car       = location.state.car
    const questions = location.state.questions

    const [question,setNextQuestion] = useState(questions[qindex]);

    useEffect( () => {
      console.log('Enter userEffect...qindex=',qindex,'answer=',answer)
      if( answer !== undefined ) {
        if(qindex < questions.length) {
            // Compute distance to go back/forth for the car
            let weight = ( questions[qindex].weight === null ) ? 1 : questions[qindex].weight
            let distance = (answer ? 1: -1) * weight
            console.log('Send AXIOS command to car for user',userid,'with distance',distance)
            let url=`http://localhost:8000/score?user_id=${userid}&weight=${distance}`
            console.log(url)
            axios.put(url)
            .then(response => {
                console.log(response.data)
            })
            .catch( error => {
                console.log(error.response)
                alert('Cannot send axios command to car for user:',userid)
            })
        }
        if( answer && (qindex === (questions.length-1))) {
            console.log('Send AXIOS command to record user time')
            // End of challenge - Record user time in DB for leaderboard display
            let url = `http://localhost:8000/end?userid=${userid}`
            console.log(url)
            axios.put(url)
            .then(response => {
                console.log(response.data)
            })
            .catch( error => {
                console.log(error.response)
                alert('Cannot record time of challenge completion for user:',userid)
            })
            alert('Congratulation, you have completed the challenge')
            navigate("/",{state:{}})
        }
      }
    }, [answer,qindex]);

    function handleOnclick(choice) {    
        console.log('Enter handleOnClick...qindex:',qindex,'answer',answer)
        let result = question.answer.includes(choice)
        if (result){
          ToggleVisibleNotVisible(question.choices)
        }
        setYourAnswer(result)
        alert(result ? 'Correct' : 'Incorrect')
    }

    function handleNextQuestion(qindex) {
      console.log('Enter handleNextQuestion...qindex:',qindex,'answer',answer)
      // New line to show back buttons after hiding them following correct answer
      ToggleVisibleNotVisible(question.choices)
      if( qindex < questions.length-1 ) {
          console.log('qindex increment')
          setQIndex(qindex+1)
          setNextQuestion(questions[qindex+1])
      }
      setYourAnswer(undefined)
    }

    // New function to hide or show choice buttons
    function ToggleVisibleNotVisible(choices){
      for(let i=0; i < choices.length; i ++){
        let x = document.getElementById(choices[i]);
        if (x.style.display === "none") {
          x.style.display = "inline";
        } else {
          x.style.display = "none";
        }
      }
    }

    return (
        <ThemeProvider theme={defaultTheme}>
        <Container>
            <Typography color="textSecondary" variant="h6">
            Welcome {firstname} to DevRel500 challenge - {car.color} car is your car color
            </Typography>
            <Container >
                <StyledImage src={question.filename} alt="" id="img" className="img" />
            </Container>
            <Container className={classes.margin}>
                <Typography color="textSecondary" variant="h6">
                Please select your answer
                </Typography>
                {question.choices.map((choice) => (
                    <AnimatedChoiceButtons id={choice} variant="contained" key={choice} onClick={() => handleOnclick(choice)}>
                    {choice}
                    </AnimatedChoiceButtons>
                ))}
                {(answer === true) && (qindex < questions.length-1) && (
                    <Button color="secondary" variant="contained" margin="10em" onClick={() => handleNextQuestion(qindex)} >
                        Next Question
                    </Button>
                )}
            </Container>
            <div className={classes.spacer} />
        </Container>
        </ThemeProvider>
    );
}

export default Challenge;