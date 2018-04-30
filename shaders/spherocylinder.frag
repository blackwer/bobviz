#version 120

varying vec4 diffuse,ambientGlobal,ambient;
varying vec3 normal,lightDir;
varying float dist;

void main()
{
    vec4 color = ambientGlobal;
    float NdotL = dot(normal,normalize(lightDir));
    if (NdotL > 0.0) {
        float att = 1.0 / (gl_LightSource[0].constantAttenuation +
                     gl_LightSource[0].linearAttenuation * dist +
                     gl_LightSource[0].quadraticAttenuation * dist * dist);
        color += att * (diffuse * NdotL + ambient);
    }
    gl_FragColor = color;
}
