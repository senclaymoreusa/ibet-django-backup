// Home components test

import React from 'react';
import { shallow } from 'enzyme';

import { Home } from '../home';

const setUp = (props={}) => {
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
      
});
 