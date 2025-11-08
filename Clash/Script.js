//PROXY=🚀 节点选择
const newRules = [
  //进程
  "PROCESS-NAME,prismlauncher.exe,🚀 节点选择",
  "PROCESS-NAME,venera.exe,🚀 节点选择",
  //CYLINK
  "DOMAIN,2cy.io,🚀 节点选择",
  "DOMAIN,次元.net,🚀 节点选择",
  //面板
  "DOMAIN,clash.razord.top,DIRECT",
  "DOMAIN,yacd.haishan.me,DIRECT",
  //规则集-代理
  "RULE-SET,proxy,🚀 节点选择",//代理域名列表 proxy.txt
  "RULE-SET,gfw,🚀 节点选择",//GFWList 域名列表 gfw.txt
  "RULE-SET,telegramcidr,🚀 节点选择",//Telegram 使用的 IP 地址列表 telegramcidr.txt
  "RULE-SET,google,🚀 节点选择",//[慎用]Google 在中国大陆可直连的域名列表 google.txt
  //"RULE-SET,tld-not-cn,🚀 节点选择",//非中国大陆使用的顶级域名列表 tld-not-cn.txt
  //规则集-直连
  "RULE-SET,lancidr,DIRECT",//局域网 IP 及保留 IP 地址列表 lancidr.txt
  "RULE-SET,cncidr,DIRECT",//中国大陆 IP 地址列表 cncidr.txt
  "RULE-SET,direct,DIRECT",//直连域名列表 direct.txt
  "RULE-SET,private,DIRECT",//私有网络专用域名列表 private.txt
  "RULE-SET,applications,DIRECT",//需要直连的常见软件列表 applications.txt
  "RULE-SET,icloud,DIRECT",//iCloud 域名列表 icloud.txt
  "RULE-SET,apple,DIRECT",//Apple 在中国大陆可直连的域名列表 apple.txt
  //规则集-丢弃
  "RULE-SET,reject,REJECT",//广告域名列表 reject.txt
  //GEOIP
  "GEOIP,LAN,DIRECT",
  "GEOIP,CN,DIRECT",
  //未匹配
  "MATCH,DIRECT",

  ];
function main(config) {
  config.rules = newRules;
  return config;
}
