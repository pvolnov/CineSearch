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
import "../css/FilmCardLong.css"
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
    showed = () => {
        var main = this;
        this.parent.setState({
            popout:
                <Alert
                    actions={[{
                        title: 'Отмена',
                        autoclose: true,
                        style: 'cancel'
                    }, {
                        title: "Да",
                        action: () => {
                            main.parent.likeFilm(main.props.film_id);
                        },
                        autoclose: true,
                    }]}
                    onClose={() => {
                        main.parent.setState({popout: null});
                    }}
                >
                    <h2>Подтверждений</h2>
                    <p>Переместить "{main.state.name}" в просмотренное?</p>
                </Alert>
        });

    };


    render() {

        return (
            <Card className={"FilmCardLong"} style={{position: "relative"}}
                  raised={true}>
                <IconButton style={{position: "absolute"}} onClick={this.deleteFilm}
                            className={"delbtn"} size="small" color="secondary">
                    <div className={"delbatton"}>
                        <Icon36Delete/>
                    </div>
                </IconButton>
                <div className={"FilmInfo"}>
                    <CardContent className={"AcideContent"}>
                        <div className={"AcideContentText"} onClick={this.onClick}>
                            <Typography component="h5" variant="h5">
                                {this.props.name}
                            </Typography>
                            <Typography component="p" color="textSecondary">
                                {this.props.about}
                            </Typography>
                        </div>

                        <div className={"navbtn"}>
                            <Button className={"btn"} onClick={this.showed} size="small" color="primary">
                                Просмотрено
                            </Button>
                        </div>
                    </CardContent>

                    <img onClick={this.onClick} className={"avatar"} onClick={this.props.onClick}
                         src={this.state.avatar}/>
                </div>
            </Card>
        )
    }
}







