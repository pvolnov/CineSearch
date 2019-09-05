import React from 'react';
import {connect} from "react-redux";
import {View, Tabbar, TabbarItem, Epic} from '@vkontakte/vkui';
import '@vkontakte/vkui/dist/vkui.css';
import Icon24Home from '@vkontakte/icons/dist/24/home';
import Icon24Like from '@vkontakte/icons/dist/24/like';
import Icon24Reorder from '@vkontakte/icons/dist/24/reorder';
import Home from './containers/Home';
import {PathToJson} from "./function";
import Film from "./containers/Film";
import Liked from "./containers/Liked";
import CineSearch from "./containers/CineSearch";
import Seed from "./containers/Seed";

class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            activeStory: 'liked',
            film_id: 0
        };

        this.params = PathToJson(window.location.hash);
        this.get = PathToJson(window.location.search);
    }


    onStoryChange = (e) => {
        this.setState({activeStory: e.currentTarget.dataset.story})
    };
    FilmSearch = () => {
        console.log("FilmSerch");
        this.setState({
            activeStory: "search"
        })
    };


    render() {
        var bar =
            <Tabbar>
                <TabbarItem
                    onClick={this.onStoryChange}
                    selected={this.state.activeStory === 'home'}
                    data-story="home"
                    text="Home"
                ><Icon24Home/></TabbarItem>
                <TabbarItem
                    onClick={this.onStoryChange}
                    selected={this.state.activeStory === 'liked'}
                    data-story="liked"
                    text="Liked"
                ><Icon24Like/></TabbarItem>
                <TabbarItem
                    onClick={this.onStoryChange}
                    selected={this.state.activeStory === 'seed'}
                    data-story="seed"
                    text="Seed"
                ><Icon24Reorder/></TabbarItem>

            </Tabbar>;
        if (this.state.activeStory === "search")
            bar = null;

        return (
            <Epic activeStory={this.state.activeStory} tabbar={bar}>
                <Home id="home" main={this}/>
                <Liked id="liked" main={this}/>
                <Seed id="seed" main={this}/>
                <CineSearch id="search" main={this}/>
            </Epic>
        );
    }
}

const mapStateToProps = (state) => {
    return {
        store: state
    };
};

export default connect(mapStateToProps)(App)
