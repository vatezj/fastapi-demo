<template>
    <div class="app-container">
      <el-form :model="queryParams" ref="queryRef" :inline="true" v-show="showSearch" label-width="68px">
        <el-form-item label="用户账号" prop="userName">
          <el-input
            v-model="queryParams.userName"
            placeholder="请输入用户账号"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="用户昵称" prop="nickName">
          <el-input
            v-model="queryParams.nickName"
            placeholder="请输入用户昵称"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="用户邮箱" prop="email">
          <el-input
            v-model="queryParams.email"
            placeholder="请输入用户邮箱"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input
            v-model="queryParams.phone"
            placeholder="请输入手机号码"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="用户性别" prop="sex">
          <el-select v-model="queryParams.sex" placeholder="请选择用户性别" clearable style="width: 240px">
            <el-option label="请选择字典生成" value="" />
          </el-select>
        </el-form-item>
    
        <el-form-item label="帐号状态" prop="status">
          <el-select v-model="queryParams.status" placeholder="请选择帐号状态" clearable style="width: 240px">
            <el-option label="请选择字典生成" value="" />
          </el-select>
        </el-form-item>
        <el-form-item label="最后登录IP" prop="loginIp">
          <el-input
            v-model="queryParams.loginIp"
            placeholder="请输入最后登录IP"
            clearable
            style="width: 240px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item label="最后登录时间" prop="loginDate">
          <el-date-picker
            v-model="queryParams.loginDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择最后登录时间"
            clearable
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">搜索</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
  
      <el-row :gutter="10" class="mb8">
        <el-col :span="1.5">
          <el-button
            type="primary"
            plain
            icon="Plus"
            @click="handleAdd"
            v-hasPermi="['app:user:add']"
          >新增</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="success"
            plain
            icon="Edit"
            :disabled="single"
            @click="handleUpdate"
            v-hasPermi="['app:user:edit']"
          >修改</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="danger"
            plain
            icon="Delete"
            :disabled="multiple"
            @click="handleDelete"
            v-hasPermi="['app:user:remove']"
          >删除</el-button>
        </el-col>
        <el-col :span="1.5">
          <el-button
            type="warning"
            plain
            icon="Download"
            @click="handleExport"
            v-hasPermi="['app:user:export']"
          >导出</el-button>
        </el-col>
        <right-toolbar v-model:showSearch="showSearch" @queryTable="getList"></right-toolbar>
      </el-row>
  
      <el-table v-loading="loading" :data="userList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column label="用户ID" align="center" prop="userId" />
        <el-table-column label="用户账号" align="center" prop="userName" />
        <el-table-column label="用户昵称" align="center" prop="nickName" />
        <el-table-column label="用户邮箱" align="center" prop="email" />
        <el-table-column label="手机号码" align="center" prop="phone" />
        <el-table-column label="用户性别" align="center" prop="sex" />
        <el-table-column label="用户头像" align="center" prop="avatar" />
        <el-table-column label="密码" align="center" prop="password" />
        <el-table-column label="帐号状态" align="center" prop="status" />
        <el-table-column label="最后登录IP" align="center" prop="loginIp" />
        <el-table-column label="最后登录时间" align="center" prop="loginDate" width="180">
          <template #default="scope">
            <span>{{ parseTime(scope.row.loginDate, '{y}-{m}-{d}') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="备注" align="center" prop="remark" />
        <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
          <template #default="scope">
            <el-button link type="primary" icon="Edit" @click="handleUpdate(scope.row)" v-hasPermi="['app:user:edit']">修改</el-button>
            <el-button link type="primary" icon="Delete" @click="handleDelete(scope.row)" v-hasPermi="['app:user:remove']">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
  
      <pagination
        v-show="total>0"
        :total="total"
        v-model:page="queryParams.pageNum"
        v-model:limit="queryParams.pageSize"
        @pagination="getList"
      />
  
      <!-- 添加或修改APP用户信息对话框 -->
      <el-dialog :title="title" v-model="open" width="500px" append-to-body>
        <el-form ref="userRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item v-if="renderField(true, true)" label="用户账号" prop="userName">
          <el-input v-model="form.userName" placeholder="请输入用户账号" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="用户昵称" prop="nickName">
          <el-input v-model="form.nickName" placeholder="请输入用户昵称" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="用户邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入用户邮箱" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="用户性别" prop="sex">
          <el-select v-model="form.sex" placeholder="请选择用户性别">
            <el-option label="请选择字典生成" value="" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="用户头像" prop="avatar">
          <el-input v-model="form.avatar" placeholder="请输入用户头像" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="密码" prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="帐号状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="请选择字典生成" value="" />
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="最后登录IP" prop="loginIp">
          <el-input v-model="form.loginIp" placeholder="请输入最后登录IP" />
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="最后登录时间" prop="loginDate">
          <el-date-picker clearable
            v-model="form.loginDate"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择最后登录时间">
          </el-date-picker>
        </el-form-item>
        <el-form-item v-if="renderField(true, true)" label="备注" prop="remark">
          <el-input v-model="form.remark" placeholder="请输入备注" />
        </el-form-item>
  
        </el-form>
        <template #footer>
          <div class="dialog-footer">
            <el-button type="primary" @click="submitForm">确 定</el-button>
            <el-button @click="cancel">取 消</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </template>
  
  <script setup name="User">
  import { listUser, getUser, delUser, addUser, updateUser } from "./api/user";
  
  const { proxy } = getCurrentInstance();
  
  const userList = ref([]);
  const open = ref(false);
  const loading = ref(true);
  const showSearch = ref(true);
  const ids = ref([]);
  const single = ref(true);
  const multiple = ref(true);
  const total = ref(0);
  const title = ref("");
  
  const data = reactive({
    form: {},
    queryParams: {
      pageNum: 1,
      pageSize: 10,
      userName: null,
      nickName: null,
      email: null,
      phone: null,
      sex: null,
      avatar: null,
      password: null,
      status: null,
      loginIp: null,
      loginDate: null,
    },
    rules: {
      userName: [
        { required: true, message: "用户账号不能为空", trigger: "blur" }
      ],
      nickName: [
        { required: true, message: "用户昵称不能为空", trigger: "blur" }
      ],
    }
  });
  
  const { queryParams, form, rules } = toRefs(data);
  
  /** 查询APP用户信息列表 */
  function getList() {
    loading.value = true;
    listUser(queryParams.value).then(response => {
      userList.value = response.rows;
      total.value = response.total;
      loading.value = false;
    });
  }
  
  /** 取消按钮 */
  function cancel() {
    open.value = false;
    reset();
  }
  
  /** 表单重置 */
  function reset() {
    form.value = {
      userId: null,
      userName: null,
      nickName: null,
      email: null,
      phone: null,
      sex: null,
      avatar: null,
      password: null,
      status: null,
      loginIp: null,
      loginDate: null,
      createBy: null,
      createTime: null,
      updateBy: null,
      updateTime: null,
      remark: null,
    };
    proxy.resetForm("userRef");
  }
  
  /** 搜索按钮操作 */
  function handleQuery() {
    queryParams.value.pageNum = 1;
    getList();
  }
  
  /** 重置按钮操作 */
  function resetQuery() {
    proxy.resetForm("queryRef");
    handleQuery();
  }
  
  /** 多选框选中数据  */
  function handleSelectionChange(selection) {
    ids.value = selection.map(item => item.userId);
    single.value = selection.length != 1;
    multiple.value = !selection.length;
  }
  
  /** 新增按钮操作 */
  function handleAdd() {
    reset();
    open.value = true;
    title.value = "添加APP用户信息";
  }
  
  /** 修改按钮操作 */
  function handleUpdate(row) {
    reset();
    const _userId = row.userId || ids.value;
    getUser(_userId).then(response => {
      form.value = response.data;
      open.value = true;
      title.value = "修改APP用户信息";
    });
  }
  
  /** 提交按钮 */
  function submitForm() {
    proxy.$refs["userRef"].validate(valid => {
      if (valid) {
        if (form.value.userId != null) {
          updateUser(form.value).then(response => {
            proxy.$modal.msgSuccess("修改成功");
            open.value = false;
            getList();
          });
        } else {
          addUser(form.value).then(response => {
            proxy.$modal.msgSuccess("新增成功");
            open.value = false;
            getList();
          });
        }
      }
    });
  }
  
  /** 删除按钮操作 */
  function handleDelete(row) {
    const _userIds = row.userId || ids.value;
    proxy.$modal.confirm('是否确认删除APP用户信息编号为"' + _userIds + '"的数据项？').then(function() {
      return delUser(_userIds);
    }).then(() => {
      getList();
      proxy.$modal.msgSuccess("删除成功");
    }).catch(() => {});
  }
  
  
  /** 导出按钮操作 */
  function handleExport() {
    proxy.download('app/user/export', {
      ...queryParams.value
    }, `user_${new Date().getTime()}.xlsx`);
  }
  
  /** 是否渲染字段 */
  function renderField(insert, edit) {
    return form.value.userId == null ? insert : edit;
  }
  
  getList();
  </script>