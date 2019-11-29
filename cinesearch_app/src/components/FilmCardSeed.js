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
import Typography from "@material-ui/core/Typography";
import "../css/FilmCardSeed.css"
import CardContent from "@material-ui/core/CardContent";
import IconButton from "@material-ui/core/IconButton";
import Icon36Delete from '@vkontakte/icons/dist/36/delete';
import {makeStyles} from '@material-ui/core/styles';
import {red} from '@material-ui/core/colors';
import Button from "@material-ui/core/Button";


export default class FilmCard extends React.Component {
    constructor(props) {
        super(props);
        this.parent = props.main;

        // this.dispatch = props.dispatch;
        var text = props.about;
        var name = props.name;
        var stext = text.slice(0, 15);
        if (stext.length < text.length) {
            stext += '...';
        }
        var sname = name.slice(0, 15);
        if (sname.length < name.length) {
            sname += '...';
        }


        this.state = {
            actPanel: "menu",//active panel
            id: props.id,//view id
            avatar: props.avatar,
            name: sname,
            about: stext,
        };

        this.onClick = () => {
            props.onClick();
        }


        this.android = platform() == "android";

    }

    deleteFilm = (e) => {
        var main = this;
        this.parent.setState({
            popout:
                <Alert
                    actions={[{
                        title: 'Отмена',
                        autoclose: true,
                        style: 'cancel'
                    }, {
                        title: "Удалить",
                        action: () => {
                            main.parent.deleteFilm(main.props.film_id);
                        },
                        autoclose: true,
                        style: "destructive"

                    }]}
                    onClose={() => {
                        main.parent.setState({popout: null});
                    }}
                >
                    <h2>Подтвердите действие</h2>
                    <p>Удалить "{main.state.name}"?</p>
                </Alert>
        });

    };



    render() {

        return (
            <Card className={"FilmCardSeed"} style={{position: "relative"}}
                  raised={true} elevation={1}>
                <IconButton style={{position: "absolute"}} onClick={this.deleteFilm}
                            className={"delbtn"} size="small" color="secondary">
                    <div className={"delbatton"}>
                        <Icon36Delete/>
                    </div>
                </IconButton>
                <div className={"FilmInfo"}>
                    <CardContent className={"ContentSeedCard"} onClick={this.onClick}>
                            <h4>
                                {this.props.name}
                            </h4>
                            <p >
                                {this.props.about}
                            </p>
                    </CardContent>

                    <img onClick={this.onClick} className={"avatar avatarSeed"}
                         src={this.state.avatar}/>
                </div>
            </Card>
        )
    }
}







