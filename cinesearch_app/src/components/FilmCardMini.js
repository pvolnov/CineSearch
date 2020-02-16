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
import CardActionArea from "@material-ui/core/CardActionArea";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import "../css/FilmBlock.css"

const itemStyle = {
    flexShrink: 0,
    display: 'flex',
    flexDirection:
        'column',
    alignItems: 'center'
};

export default class FilmCard extends React.Component {
    constructor(props) {
        super(props);
        // this.store = props.store;
        // this.dispatch = props.dispatch;
        var text = props.name;
        var sliced = text.slice(0,15);
        if (sliced.length < text.length) {
            sliced += '...';
        }

        this.state = {
            actPanel: "menu",//active panel
            id: props.id,//view id
            popuot: null,
            name:sliced,
            avatar:props.avatar
        };

        this.android = platform() == "android";

    }



    render() {


        //upload our records

        return (
            <Card className={"filmcardmini"} style={itemStyle}>
                <CardActionArea >
                    <img src={this.state.avatar}
                    className={"avatarmini"}/>
                    <div className={"filmnamemini"}>

                    <Typography  variant="body2" color="textSecondary" component="p">
                        <span>{this.state.name}</span>
                    </Typography>
                    </div>

                </CardActionArea>
            </Card>
        )
    }
}







