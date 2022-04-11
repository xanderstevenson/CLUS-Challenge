import { useNavigate } from 'react-router-dom';
import Button from "@material-ui/core/Button";

const Instructions = () => {
    const navigate = useNavigate();

    return (
        <div>
            <Button onClick={() => {navigate("/")}}>
                {" "}
                Click to jump to main page 
            </Button>
        </div>
    );
}

export default Instructions