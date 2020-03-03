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
import CardActionArea from "@material-ui/core/CardActionArea";
import Typography from "@material-ui/core/Typography";
import "../css/FilmPage.css"

const itemStyle = {
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
            photo:props.photo,
            href:props.href
        };

        this.android = platform() == "android";

    }



    render() {


        //upload our records

        return (
            <Card className={"actorcard"} onClick={()=>window.open(this.state.href, '_blank')}
                  style={itemStyle}>
                <CardActionArea >
                    <img src={this.state.photo}
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







