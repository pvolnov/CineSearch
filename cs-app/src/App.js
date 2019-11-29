import React from 'react';
import '@vkontakte/vkui/dist/vkui.css';
import {Epic} from "@vkontakte/vkui";
import Home from './containers/CineSearch';
import {PathToJson} from "./function";

export default class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            activeStory: 'home',
            film_id: 0
        };

        this.params = PathToJson(window.location.hash);
        this.get = PathToJson(window.location.search);
    }


    render() {
        return (

            <Epic activeStory={this.state.activeStory}>
                <Home id="home" main={this}/>
            </Epic>
        );
    }
}


