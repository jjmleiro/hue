## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.    See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
  from desktop import conf
  from django.utils.translation import ugettext as _
  from desktop.views import commonheader, commonfooter
%>

${ commonheader("Welcome to Hue", "login", user, "50px") | n,unicode }

<link rel="stylesheet" href="/static/ext/chosen/chosen.min.css">
<style type="text/css">  
  @font-face {
    font-family: OpenSansLight;
    src: url("/static/ext/fonts/isban/OpenSans-Light.ttf");
  }

  @font-face {
    font-family: OpenSansRegular;
    src: url("/static/ext/fonts/isban/OpenSans-Regular.ttf");
  }

  @font-face {
    font-family: OpenSansSemiBold;
    src: url("/static/ext/fonts/isban/OpenSans-Semibold.ttf");
  }

  @font-face {
    font-family: OpenSansBold;
    src: url("/static/ext/fonts/isban/OpenSans-Bold.ttf");
  }

  body {    
    font-family: OpenSansRegular;
    height: 100%;    
  }

  @-webkit-keyframes spinner {
    from {
      -webkit-transform: rotateY(0deg);
    }
    to {
      -webkit-transform: rotateY(-360deg);
    }
  }

  #logo {
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 10px;
    background: url("/static/art/isban/logo-principal-white.png") 50% 2px no-repeat;
    width: 360px;
    height: 114px;
  }

  #logo.waiting {
    -webkit-animation-name: spinner;
    -webkit-animation-timing-function: linear;
    -webkit-animation-iteration-count: infinite;
    -webkit-animation-duration: 2s;
    -webkit-transform-style: preserve-3d;
  }

  .table-height {
    height: 385px;
    overflow:hidden;
  }

  .login-content {    
    width: 500px;    
  }

  .input-prepend {
    width: 100%;
  }

  .input-prepend .add-on {
    min-height: 38px;
    line-height: 38px;
    color: #999;
  }

  .login-content input {
    width: 85%;
    min-height: 38px;
    font-size: 18px;
  }

  .login-content .input-prepend.error input, .login-content .input-prepend.error .add-on {
    border-top-color: #444444;
    border-bottom-color: #444444;
  }

  .login-content .input-prepend.error input {
    border-right-color: #444444;
  }

  .login-content .input-prepend.error .add-on {
    border-left-color: #444444;
  }

  .login-content input[type='submit'] {
    height: 44px;
    min-height: 44px;
    font-weight: normal;
    text-shadow: none;
  }

  hr {
    border-top-color: #DEDEDE;
  }

  ul.errorlist {
    text-align: left;
    margin-bottom: 4px;
    margin-top: -4px;
  }

  .alert-error ul.errorlist {
    text-align: center;
    margin-top: 0;
  }

  ul.errorlist li {
    font-size: 13px;
    font-weight: normal;
    font-style: normal;
  }

  input.error {
    border-color: #b94a48;
    -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    -moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
    box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
  }

  .well {
    border: 1px solid #D8D8D8;
    border-radius: 3px 3px 3px 3px;
    background-color: #EC0000;
  }

  .footer {
    position: fixed;
    bottom: 0;
    background-color: #338BB8;
    height: 6px;
    width: 100%;
  }

  h3 {
    font-family: OpenSansBold;
    color: #191919;
    font-size: 24px;
    font-weight: 400;
    margin-bottom: 20px;
  }

  .chosen-single {
    min-height: 38px;
    text-align: left;
    font-size: 18px;
  }

  .chosen-single span {
    display: inline;
    line-height: 38px;
    vertical-align: middle;
  }

  .chosen-container-active.chosen-with-drop .chosen-single div b,
  .chosen-container-single .chosen-single div b {
    background-position-x: 1px;
    background-position-y: 10px;
  }

  .chosen-container-active.chosen-with-drop .chosen-single div b {
    background-position-x: -17px;
    background-position-y: 10px;
  }

  #tblLogin {
    margin-top: 80px;    
  }

</style>

<div class="footer"></div>

<table id="tblLogin" width="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td align="right">
      <div class="login-content center table-height">      

        <form method="POST" action="${action}" class="well">
          
          <div id="logo"></div>

          %if first_login_ever:
            <h3>${_('Create your Hue account')}</h3>
          %else:
            <h3>${_('Sign in to continue to Hue')}</h3>
          %endif

          %if first_login_ever:
            <div class="alert alert-block">
              ${_('Since this is your first time logging in, pick any username and password. Be sure to remember these, as')}
              <strong>${_('they will become your Hue superuser credentials.')}</strong>.
            </div>
          %endif

          <div class="input-prepend
            % if backend_name == 'OAuthBackend':
              hide
            % endif
          ">
            <span class="add-on"><i class="fa fa-user"></i></span>
            ${ form['username'] | n,unicode }
          </div>

          ${ form['username'].errors | n,unicode }

          <div class="input-prepend
            % if backend_name in ('AllowAllBackend', 'OAuthBackend'):
              hide
            % endif
          ">
            <span class="add-on"><i class="fa fa-lock"></i></span>
            ${ form['password'] | n,unicode }
          </div>
          ${ form['password'].errors | n,unicode }

          %if active_directory:
          <div class="input-prepend">
            <span class="add-on"><i class="fa fa-globe"></i></span>
            ${ form['server'] | n,unicode }
          </div>
          %endif

          %if login_errors and not form['username'].errors and not form['password'].errors:
            <div class="alert alert-error" style="text-align: center">
              <strong><i class="fa fa-exclamation-triangle"></i> ${_('Error!')}</strong>
              % if form.errors:
                % for error in form.errors:
                 ${ form.errors[error]|unicode,n }
                % endfor
              % endif
            </div>
          %endif
          <br/>
          %if first_login_ever:
            <br/>
            <input type="submit" class="btn btn-login" value="${_('Create account')}"/>
          %else:
            <br/>
            <input type="submit" class="btn btn-login" value="${_('Sign in')}"/>
          %endif
          <input type="hidden" name="next" value="${next}"/>
        </form>
      </div>
    </td>
    <td align="left">
      <div class="table-height">
        <img src="/static/art/isban/fondo.png" height="100%" width="100%"/>
      </div>
    </td>
  </tr>
</table>

<script src="/static/ext/chosen/chosen.jquery.min.js" type="text/javascript" charset="utf-8"></script>

<script>
  $(document).ready(function () {
    $("#id_server").chosen({
      disable_search_threshold: 5,
      width: "90%",
      no_results_text: "${_('Oops, no database found!')}"
    });

    $("form").on("submit", function () {
      window.setTimeout(function () {
        $("#logo").addClass("waiting");
      }, 1000);
    });

    % if backend_name == 'AllowAllBackend':
      $('#id_password').val('password');
    % endif

    % if backend_name == 'OAuthBackend':
      $("input").css({"display": "block", "margin-left": "auto", "margin-right": "auto"});
      $("input").bind('click', function () {
        window.location.replace('/login/oauth/');
        return false;
      });
    % endif

    $("ul.errorlist").each(function () {
      $(this).prev().addClass("error");
    });
  });
</script>

${ commonfooter(messages) | n,unicode }