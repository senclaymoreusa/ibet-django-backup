import React from 'react';
import { shallow } from 'enzyme';

import { Home } from '../home';
import { Navigation } from '../navigation';
import { NavLink } from 'react-router-dom';

const setUp = (props={}) => {
    // localStorage.setItem('token', "12345");
    const authCheckState = jest.fn();
    const component = shallow(<Home authCheckState={authCheckState} />);
    return component;
};

const findByTestAtrr = (component, attr) => {
    const wrapper = component.find(`[data-test='${attr}']`);
    return wrapper;
};

describe('Home Component', () => {

    let component;
    beforeEach(() => {
        component = setUp();
    });

    //Snapshot Test
    it('should render without throwing an error', () => {
        expect(component).toMatchSnapshot();
    });

    //Components Test
    it('should have one header', () => {

        const wrapper = findByTestAtrr(component, 'headerLine');
        expect(wrapper.length).toBe(1);
    });

    

    it('should render a H1', () => {
        const h1 = findByTestAtrr(component, 'header');
        expect(h1.length).toBe(1);
    });

    //Testing User Interactive Event
    it('should call mock function when button is clicked', () => {
        const wrapper = shallow(<Navigation lang ={'en'}/>);
        expect(wrapper.find(NavLink).first().props().to).toEqual('/');
    });
      
});
 