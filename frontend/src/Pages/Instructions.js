import { useNavigate } from 'react-router-dom';
import { Button } from '../components/styles/Button.styled'

const Instructions = () => {
    const navigate = useNavigate();

    return (
        <Button onClick={() => {navigate("/")}}>
            {" "}
            Click to jump to home page
        </Button>
    );
}

export default Instructions