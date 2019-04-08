// import React from 'react';
// import renderer from 'react-test-renderer';
// import Login from '../login';


// describe('<Login /> rendering', () => {
//     // let wrapper;
//     // beforeEach(() => {
//     //     wrapper = shallow(<Login/>);
//     // });
//     it('renders correctly', () => {
//         // const TextInputComponent = renderer.create(<Login />).toJSON();
//         let wrapper = shallow(<Login Component/>);
//         // expect(wrapper.find('form'));
//         expect(wrapper).toMatchSnapshot();
//     });
//     // it('renders correctly', () => {
//     //     expect(wrapper).toMatchSnapshot();
//     // });
// });


import React from 'react';
import { shallow, mount, render } from 'enzyme';
import LoginTest from '../logintest';
import { Login } from '../login';
import { Home } from '../home';
import renderer from 'react-test-renderer';

describe('Login Component', () => {
    
    // it('should render without throwing an error', () => {
    //     const wrapper = renderer
    //     .create(<Login />)
    //     .toJSON();
    //     expect(wrapper).toMatchSnapshot();
    //     // expect(wrapper).exists(<form className='login'></form>).toBe(true);
    // })

    // it('should render without throwing an error', () => {
    //     const wrapper = shallow(<Login />);
    //     expect(wrapper).toMatchSnapshot();
    //     // expect(wrapper).exists(<form className='login'></form>).toBe(true);
    // })

    it('should render without throwing an error', () => {
        // expect(shallow(<LoginTest />).exists(<form></form>)).toBe(true);
        const wrapper = shallow(<Home />);
        
        expect(wrapper).toMatchSnapshot();
    })
    it('renders a email input', () => {
        expect(shallow(<LoginTest />).find('#email').length).toEqual(1)
    })
    it('renders a password input', () => {
        expect(shallow(<LoginTest />).find('#password').length).toEqual(1)
    })
 
   describe('Email input', () => {
  
    it('should respond to change event and change the state of the Login Component', () => {
     const wrapper = shallow(<LoginTest />)
     wrapper.find('#email').simulate('change', {target: {name: 'email', value: 'blah@gmail.com'}})
     expect(wrapper.state('email')).toEqual('blah@gmail.com')
    })
   })
 
   describe('Password input', () => {
  
    it('should respond to change event and change the state of the Login Component', () => {
     const wrapper = shallow(<LoginTest />)
     wrapper.find('#password').simulate('change', {target: {name: 'password', value: 'cats'}})
     expect(wrapper.state('password')).toEqual('cats')
    })
   })
})