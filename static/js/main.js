var NombreUsuario = ''

// signin
const signinform = document.querySelector('#login-form');

signinform.addEventListener('submit', e => {
    e.preventDefault();
    const email = document.querySelector('#login-email').value;
    const password = document.querySelector('#login-password').value;
    //console.log(email, password)

    auth
        .signInWithEmailAndPassword(email, password)
        .then(UserCredential => {
            //clear the form
            signinform.reset();
            // signupForm.querySelector('.error').innerHTML = '';

            //close the modal
            $('#signinModal').modal('hide');
            MandarForm = "1"

            //console.log('sign in')
        })
        .catch(err => {
            signinform.querySelector('.errorForm').innerHTML = err.message;
        });
})

// Google Login
const buttonGoogle = document.querySelector("#googleLogin")
buttonGoogle.addEventListener('click', e => {
    console.log('click google')
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then(result => {
            console.log('google sign in')
            // console.log('valor google mandarform')
            // console.log(MandarForm)
            $("#login-email").val(NombreUsuario)
            $("#login-form").submit()
			// window.location.href = '/'
        })
        .catch(err => {
            console.log(err)
        })
})

// LogOut
const logout = document.querySelector("#logout");

logout.addEventListener('click', e => {
    e.preventDefault();
    auth.signOut().then(() => {
        console.log('log out')
        console.log('borrando nombre usuario')
        NombreUsuario=''
        MandarForm="0"
        console.log('valor final nombreusuario')
        console.log(NombreUsuario);
        console.log('valor final mandarform')
        console.log(MandarForm)
        location.href = '/logout';
    })
})


//Events user
auth.onAuthStateChanged(user =>{
    if(user) {
        console.log('estado usuario: sign in')
        NombreUsuario = user.email;
        loginCheck(user);
    } else {
        console.log('estado usuario: log out')
        loginCheck(user);
    }
})