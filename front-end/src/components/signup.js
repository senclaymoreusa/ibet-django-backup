import React from 'react';
import { Form, Input, Icon, Button } from 'antd';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { authSignup } from '../actions'

const FormItem = Form.Item;

class RegistrationForm extends React.Component {
  state = {
    confirmDirty: false,
  };

  handleSubmit = (e) => {
    e.preventDefault();
    this.props.form.validateFieldsAndScroll((err, values) => {
      if (!err) {
        this.props.authSignup(
            values.userName,
            values.email,
            values.password,
            values.confirm,
            values.first_name,
            values.last_name,
            values.phone,
            values.date_of_birth,
            values.street_address_1,
            values.street_address_2,
            values.country,
            values.city,
            values.zipcode,
            values.state
        );
        this.props.history.push('/');
      }
    });
  }

  handleConfirmBlur = (e) => {
    const value = e.target.value;
    this.setState({ confirmDirty: this.state.confirmDirty || !!value });
  }

  compareToFirstPassword = (rule, value, callback) => {
    const form = this.props.form;
    if (value && value !== form.getFieldValue('password')) {
      callback('Two passwords that you enter is inconsistent!');
    } else {
      callback();
    }
  }

  validateToNextPassword = (rule, value, callback) => {
    const form = this.props.form;
    if (value && this.state.confirmDirty) {
      form.validateFields(['confirm'], { force: true });
    }
    callback();
  }

  render() {
    const { getFieldDecorator } = this.props.form;

    return (
      <Form onSubmit={this.handleSubmit}>
        
        <FormItem>
            {getFieldDecorator('userName', {
                rules: [{ required: true, message: 'Please input your username!' }],
            })(
                <Input prefix={<Icon type="user" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Username" />
            )}
        </FormItem>
        
        <FormItem>
          {getFieldDecorator('email', {
            rules: [{
              type: 'email', message: 'The input is not valid E-mail!',
            }, {
              required: true, message: 'Please input your E-mail!',
            }],
          })(
            <Input prefix={<Icon type="mail" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Email" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('password', {
            rules: [{
              required: true, message: 'Please input your password!',
            }, {
              validator: this.validateToNextPassword,
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} type="password" placeholder="Password" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('confirm', {
            rules: [{
              required: true, message: 'Please confirm your password!',
            }, {
              validator: this.compareToFirstPassword,
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} type="password" placeholder="Password" onBlur={this.handleConfirmBlur} />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('first_name', {
            rules: [{
              required: true, message: 'First name is required!',
            }],
          })(
            <Input prefix={<Icon type="smile" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="First name" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('last_name', {
            rules: [{
              required: true, message: 'Last name is required!',
            }],
          })(
            <Input prefix={<Icon type="smile" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="last name" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('phone', {
            rules: [ {
              required: true, message: 'Phone number is required!',
            }],
          })(
            <Input prefix={<Icon type="phone" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Phone" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('date_of_birth', {
            rules: [{
              required: true, message: 'Date of birth is required!',
            }],
          })(
            <Input prefix={<Icon type="calendar" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Date of birth" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('street_address_1')(
            <Input prefix={<Icon type="home" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Street address 1" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('street_address_2')(
            <Input prefix={<Icon type="home" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Street address 2" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('city', {
            rules: [{
              required: true, message: 'City is required!',
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="city" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('state', {
            rules: [{
              required: true, message: 'State is requiredl!',
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="state" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('country', {
            rules: [{
              required: true, message: 'Country is required!',
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="country" />
          )}
        </FormItem>

        <FormItem>
          {getFieldDecorator('zipcode', {
            rules: [{
              required: true, message: 'Zipcode is required!',
            }],
          })(
            <Input prefix={<Icon type="lock" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="zipcode" />
          )}
        </FormItem>

        <FormItem>
        <Button type="primary" htmlType="submit" style={{marginRight: '10px'}}>
            Signup
        </Button>
        Or 
        <NavLink 
            style={{marginRight: '10px', textDecoration: 'none'}} 
            to='/login/'> Login
        </NavLink>
        </FormItem>

      </Form>
    );
  }
}

const Sign = Form.create()(RegistrationForm);

const mapStateToProps = (state) => {
    return {
        loading: state.loading,
        error: state.error
    }
}

export default connect(mapStateToProps, {authSignup})(Sign);