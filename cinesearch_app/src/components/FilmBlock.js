import React from 'react';
import {
    Alert,
    Cell,
    CellButton,
    Div,
    Footer,
    Group,
    HeaderButton,
    HeaderContext,
    List,
    Panel,
    PanelHeader,
    PanelHeaderContent,
    platform,
    ScreenSpinner,
    View
} from '@vkontakte/vkui';

import Card from "@material-ui/core/Card";
import CardMedia from "@material-ui/core/CardMedia";
import CardActions from "@material-ui/core/CardActions";
import Button from "@material-ui/core/Button";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import "../css/FilmBlock.css"
import MoreVertIcon from '@material-ui/icons/MoreVert';
import IconButton from "@material-ui/core/IconButton";

export default class FilmBlock extends React.Component {
    constructor(props) {
        super(props);
        // this.store = props.store;
        // this.dispatch = props.dispatch;

        this.state = {
            actPanel: "menu",//active panel
            id: props.id,//view id
            popuot: null
        };

        this.android = platform() == "android";

    }



    render() {

        //upload our records

        return (
            <Card className={"filmcard"} onClick={this.props.onClick}>
                <CardActionArea >
                    <CardMedia
                        className={"avatar"}
                        title="Film Avatar"
                        image="https://www.wallpaperup.com/uploads/wallpapers/2018/03/22/1234615/3d0e59d12222626b5f8c7de5c77c8549-1000.jpg"
                    />
                    <CardContent>
                        <Typography gutterBottom variant="h5" component="h2">
                            Подобрать фильм
                        </Typography>
                        <Typography component="p">
                            Выбирете один из 100 000 фильмов всего за пару минут
                        </Typography>
                    </CardContent>

                </CardActionArea>
            </Card>
        )
    }
}







