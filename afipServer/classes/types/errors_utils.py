from collections import namedtuple
# from soap_util import FE


# simulate AFIP's errors
Error = namedtuple('Error', ['code', 'msg'])

# simulate AFIP's observations
Observation = namedtuple('Observation', ['code', 'msg'])



class InvalidRequest(Exception):
    """Used to create responses that simulate AFIP's errors and observations."""

    def __init__(self, errors=None, observations=None):
        self.errors, self.observations = errors or [], observations or []
        errors_str = '\n'.join(map(lambda error: '\t%s: %s' % (error.code, error.msg), self.errors))
        observations_str = '\n'.join(map(lambda observation: '\t%s: %s' % (observation.code, observation.msg), self.observations))
        msg = ''
        if len(errors_str) > 0:
            msg += 'Errors:\n%s\n' % errors_str
        if len(observations_str) > 0:
            msg += 'Observations:\n%s\n' % observations_str
        Exception.__init__(self, msg)


def errors_serialize(errors, observations):
    """Serializes the errors and observations in the format used by AFIP responses."""

    errors_serialized = []
    for error in errors:
        errors_serialized.append(FE.Err(
            FE.Code(error.code),
            FE.Msg(error.msg)
        ))
    errors_serialized = FE.Errors(
        *errors_serialized
    )
    observations_serialized = []
    for observation in observations:
        observations_serialized.append(
            FE.Obs(
                FE.Code(observation.code),
                FE.Msg(observation.msg)
            )
        )
    observations_serialized = FE.Observaciones(
        *observations_serialized
    )

    return errors_serialized, observations_serialized
