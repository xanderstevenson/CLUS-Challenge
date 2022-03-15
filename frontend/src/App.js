
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Welcome screen before displaying the first question
const url = 'https://pubhub.devnetcloud.com/media/devnetcreate-challenge-2021/site/images/devvie-on-homepage.png'
// Index to the current question
let index = 0

const App = () => {
	const [question,setImage] = useState(url)
	const [questionList,setQuestionList] = useState('')

	useEffect( () => {
		if( questionList === '' ) {
			axios.get('http://localhost:8000/questions')
			.then (response => {
				setQuestionList(response.data)
			})
			.catch(error => {
				console.error("Error fetching quetions from database")
			})
		}
	}, []);

	const imageHandler = (e) => {
		if (index < questionList.length) {
			setImage(questionList[index].filename)
			index = index + 1
		} else {
			alert('Congratulation, you have completed the challenge!')
		}
	}

	return (
		<div className="page">
			<div className="container">
				<h1 className="heading">CLUS Demo Question</h1>
				<div className="img-holder">
					<img src={question} alt="" id="img" className="img" />
				</div>
				<button className="image-upload" onClick={imageHandler}>Next question</button>
			</div>
		</div>
	)
}

export default App;