class APIPath:
    # IV WAS
    # GET
    R_DID = '/v1/did/'
    GET_VC = '/v1/credential'
    IS_VALID_VC = '/v1/credential/isValid'

    # POST
    C_DID = '/v1/did/create'
    U_DID = '/v1/did/update'
    REG_VC = '/v1/credential/register'
    REV_VC = '/v1/credential/revoke'

    ISS_VC_LOG = '/v1/log/issueCredential'
    ISS_VP_LOG = '/v1/log/issuePresentation'
    VRF_VP_LOG = '/v1/log/verifyPresentation'
