using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace FileServiceClientExpr
{
    public class DataObjectMapping<T>
    {
        public string Root { get; set; }
        public T Fields { get; }

        public DataObjectMapping(string root)
        {
            this.Root = root;
        }

        public DataObjectMapping()
        {
        }
    }
    public class Builder
    {
        static Hashtable expr_mapping => new Hashtable {
            {ExpressionType.Equal,"$eq" },
            {ExpressionType.NotEqual,"$ne" },
            {ExpressionType.LessThan,"$lt" },
            {ExpressionType.LessThanOrEqual,"$lte" },
            {ExpressionType.GreaterThan,"$gt" },
            {ExpressionType.GreaterThanOrEqual,"$gte" }
        };
        [System.Diagnostics.DebuggerStepThrough]
        public static PField Field(string FieldName)
        {
            return new PField(FieldName);
        }
        [System.Diagnostics.DebuggerStepThrough]
        public static Hashtable Parse(Expression<Func<object, bool>> Expr)
        {
            return Serilize(Expr as LambdaExpression) as Hashtable;
        }
        [System.Diagnostics.DebuggerStepThrough]
        private static object Serilize(Expression expr)
        {
            if (expr is LambdaExpression)
            {
                return Serilize(((LambdaExpression)expr).Body);
            }
            if ((expr is BinaryExpression) && (
                                                 ((BinaryExpression)expr).NodeType == ExpressionType.AndAlso
                                                || ((BinaryExpression)expr).NodeType == ExpressionType.OrElse))
            {
                var bx = expr as BinaryExpression;
                var left = Serilize(bx.Left);
                var right = Serilize(bx.Right);
                if (bx.NodeType == ExpressionType.AndAlso)
                {
                    return new Hashtable()
                    {
                        {
                            "$and", new object[]{left,right}

                        }
                    };
                }
                if (bx.NodeType == ExpressionType.OrElse)
                {
                    return new Hashtable()
                    {
                        {
                            "$or", new object[]{left,right}

                        }
                    };
                }
                throw new NotImplementedException();
            }
            if (expr is BinaryExpression)
            {
                var bExpr = expr as BinaryExpression;
                var left = Serilize(bExpr.Left);
                var right = Serilize(bExpr.Right);
                var op = GetOp(bExpr.NodeType);
                if (left is Hashtable)
                {
                    var h = left as Hashtable;
                    var fx = h.Cast<DictionaryEntry>().ToList();
                    if (fx.Count > 0 && fx[0].Key is string && fx[0].Key.ToString().StartsWith("$$"))
                    {
                        h["$value"] = right;
                        return new Hashtable()
                        {
                            {
                                op, h
                            }
                        };
                    }

                }
                else if (left is PField)
                {
                    return new Hashtable
                    {
                        {
                            op, new Hashtable
                            {
                                { ((PField)left).name,right }
                            }
                        }
                    };
                }
                else if (left is CallFunction)
                {
                    var cf = left as CallFunction;
                    return new Hashtable
                    {
                        { op, new Hashtable
                                {
                                    { cf.FuncName,cf.FieldPath  },
                                    { "$value",right }
                                }
                        }
                    };
                }
                return new Hashtable
                {
                    {left, new Hashtable
                        {
                            { op, right }
                        }
                    }
                };

            }
            if (expr is MethodCallExpression)
            {
                var cExpr = expr as MethodCallExpression;
                if (cExpr.Method == typeof(Builder).GetMethod(nameof(Field)))
                {
                    if ((cExpr.Arguments.Count() == 1) && (cExpr.Arguments[0] is ConstantExpression))
                    {
                        var constExpr = cExpr.Arguments[0] as ConstantExpression;
                        return constExpr.Value;

                    }

                }
                if (cExpr.Method == typeof(PField).GetMethod(nameof(PField.Contains)))
                {
                    if (cExpr.Object is MethodCallExpression)
                    {
                        var fx = cExpr.Object as MethodCallExpression;
                        if (fx.Method == typeof(Builder).GetMethod(nameof(Builder.Field)))
                        {

                            var fieldName = resolve(fx.Arguments[0]);
                            return new Hashtable()
                            {
                                {
                                    "$$contains", new Hashtable()
                                    {
                                        { "$field",fieldName },
                                        { "$value", resolve(cExpr.Arguments[0]) }
                                    }
                            } };

                        }
                    }



                }
                if (cExpr.Object is MethodCallExpression)
                {

                    var fx = cExpr.Object as MethodCallExpression;
                    if (fx.Method == typeof(Builder).GetMethod(nameof(Builder.Field)))
                    {
                        if (cExpr.Method == typeof(PField).GetMethod(nameof(PField.GetYear)))
                        {

                            return new Hashtable()
                            {
                                {
                                    "$$year",resolve(fx.Arguments[0])
                                }
                            };
                        }
                        else if (cExpr.Method == typeof(PField).GetMethod(nameof(PField.GetMonth)))
                        {

                            return new Hashtable()
                            {
                                {
                                    "$$month",resolve(fx.Arguments[0])
                                }
                            };
                        }
                        else if (cExpr.Method == typeof(PField).GetMethod(nameof(PField.GetDay)))
                        {

                            return new Hashtable()
                            {
                                {
                                    "$$day",resolve(fx.Arguments[0])
                                }
                            };
                        }
                        return resolve(fx.Arguments[0]);
                    }
                }

            }
            if (expr is ConstantExpression)
            {
                var constExpr = expr as ConstantExpression;
                return constExpr.Value;
            }
            if (expr is MemberExpression)
            {
                var fielPath = "";
                var mExpr = expr as MemberExpression;
                if (mExpr.Expression.Type == typeof(DateTime) && mExpr.Type == typeof(int))
                {
                    return resovle_datetime_expr(mExpr);
                }
                if (IsMapping(mExpr, ref fielPath))
                {
                    return fielPath.TrimStart('.');
                }

                if (mExpr.Expression is MethodCallExpression)
                {
                    var cx = mExpr.Expression as MethodCallExpression;
                    if (cx.Method == typeof(Builder).GetMethod(nameof(Field)))
                    {
                        var propertyInfo = mExpr.Member;
                        if (propertyInfo.Name == "Value" && propertyInfo == typeof(PField).GetProperty("Value"))
                        {
                            return ((mExpr.Expression as MethodCallExpression).Arguments[0] as ConstantExpression).Value;
                        }
                    }
                }

            }
            if (expr is NewArrayExpression)
            {
                var naExpr = expr as NewArrayExpression;
                var ret = new List<object>();
                foreach (var x in naExpr.Expressions)
                {
                    ret.Add(Builder.resolve(x));
                }

                return ret;

            }
            if (expr is MemberExpression)
            {
                return Builder.resolve(expr);
            }
            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Method.DeclaringType == typeof(PField) && ((MethodCallExpression)expr).Method.Name == nameof(PField.GetYear))
            {
                var cx = ((MethodCallExpression)expr);
                var left = Serilize(cx.Object);

                if (left is string)
                {
                    return new Hashtable()
                    {
                        { "$$year",left }
                    };
                }
                else if (left is PField)
                {
                    return new Hashtable()
                    {
                        { "$$year",((PField)left).name }
                    };
                }
                else
                {
                    throw new NotImplementedException();
                }
            }
            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Method.DeclaringType == typeof(PField) && ((MethodCallExpression)expr).Method.Name == nameof(PField.GetMonth))
            {
                var cx = ((MethodCallExpression)expr);
                var left = Serilize(cx.Object);

                if (left is string)
                {
                    return new Hashtable()
                    {
                        { "$$month",left }
                    };
                }
                else if (left is PField)
                {
                    return new Hashtable()
                    {
                        { "$$month",((PField)left).name }
                    };
                }
                else
                {
                    throw new NotImplementedException();
                }
            }
            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Method.DeclaringType == typeof(PField) && ((MethodCallExpression)expr).Method.Name == nameof(PField.GetDay))
            {
                var cx = ((MethodCallExpression)expr);
                var left = Serilize(cx.Object);

                if (left is string)
                {
                    return new Hashtable()
                    {
                        { "$$day",left }
                    };
                }
                else if (left is PField)
                {
                    return new Hashtable()
                    {
                        { "$$day",((PField)left).name }
                    };
                }
                else
                {
                    throw new NotImplementedException();
                }
            }

            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Method.DeclaringType == typeof(string) && ((MethodCallExpression)expr).Method.Name == nameof(string.StartsWith))
            {
                var cx = ((MethodCallExpression)expr);
                var left = Serilize(cx.Object);
                var right = resolve(cx.Arguments[0]);
                if (left is string)
                {
                    return new Hashtable()
                    {
                        { "$eq", new Hashtable
                            {
                                { "$$first",left },
                                {"$value",right }
                            }
                        }
                    };
                }
                else if (left is PField)
                {
                    return new Hashtable()
                    {
                        { "$eq", new Hashtable
                            {
                                { "$$first",((PField)left).name },
                                {"$value",right }
                            }
                        }
                    };
                }
                else
                {
                    throw new NotImplementedException();
                }
            }
            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Method.DeclaringType == typeof(string) && ((MethodCallExpression)expr).Method.Name == nameof(string.EndsWith))
            {
                var cx = ((MethodCallExpression)expr);
                var left = Serilize(cx.Object);
                var right = resolve(cx.Arguments[0]);
                if (left is string)
                {
                    return new Hashtable()
                    {
                        { "$eq", new Hashtable
                            {
                                { "$$last",left },
                                {"$value",right }
                            }
                        }
                    };
                }
                else if (left is PField)
                {
                    return new Hashtable()
                    {
                        { "$eq", new Hashtable
                            {
                                { "$$last",((PField)left).name },
                                {"$value",right }
                            }
                        }
                    };
                }
                else
                {
                    throw new NotImplementedException();
                }
            }
            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Method.DeclaringType == typeof(string) && ((MethodCallExpression)expr).Method.Name == nameof(string.Contains))
            {
                var cx = ((MethodCallExpression)expr);
                var left = Serilize(cx.Object);
                var right = resolve(cx.Arguments[0]);
                if (left is string)
                {
                    return new Hashtable()
                    {
                        { "$$contains", new Hashtable
                            {
                                { "$field",left },
                                {"$value",right }
                            }
                        }
                    };
                }
                else if (left is PField)
                {
                    return new Hashtable()
                    {
                        { "$eq", new Hashtable
                            {
                                { "$$contains",((PField)left).name },
                                {"$value",right }
                            }
                        }
                    };
                }
                else
                {
                    throw new NotImplementedException();
                }
            }
            if (expr is MethodCallExpression && ((MethodCallExpression)expr).Object is MemberExpression)
            {
                var mb = ((MethodCallExpression)expr).Object as MemberExpression;
                if (mb.Type == typeof(PField))
                {
                    return resolve(mb);
                }

            }
            if (expr.NodeType == ExpressionType.Convert)
            {
                return Serilize(((UnaryExpression)expr).Operand);
            }
            if (expr.NodeType == ExpressionType.Call)
            {
                var mc = expr as MethodCallExpression;
                if (mc.Method.DeclaringType == typeof(Builder) && mc.Method.Name == nameof(Builder.Search))
                {
                    var content = resolve(mc.Arguments[0]);
                    var fields = new List<object>();
                    for (var i = 1; i < mc.Arguments.Count; i++)
                    {
                        fields.AddRange(resolve(mc.Arguments[i]) as object[]);
                    }
                    /**
                     * "$$search": {
                          "$fields": [
                            "content"
                          ],
                          "$value": "long test"
                        }
                     */
                    return new Hashtable()
                    {
                        {
                            "$$search", new Hashtable() {
                                {
                                    "$fields", fields.ToArray()
                                },
                                {
                                    "$value",content
                                }
                            }
                        }
                    };

                }
            }
            throw new NotImplementedException();
        }
        /// <summary>
        /// Boost value search or like
        /// </summary>
        /// <param name="fileName"></param>
        /// <param name="BoostValue"></param>
        /// <returns></returns>
        [System.Diagnostics.DebuggerStepThrough]
        public static object Boost(object fileName, int BoostValue)
        {
            throw new NotImplementedException();
        }
        /// <summary>
        /// Do search in Elastic Search
        /// </summary>
        /// <param name="Content"></param>
        /// <param name="Fields"></param>
        /// <returns></returns>
        [System.Diagnostics.DebuggerStepThrough]
        public static bool Search(string Content, params object[] Fields)
        {
            throw new NotImplementedException();
        }
        [System.Diagnostics.DebuggerStepThrough]
        public static Expression<Func<T, bool>> Or<T>(params Expression<Func<T, bool>>[] Exprs)
        {
            var x = Exprs[0];
            for(var i=1;i< Exprs.Length; i++)
            {
                if (x != null)
                {
                    x = Expression.Lambda<Func<T, bool>>(Expression.OrElse(x.Body, Exprs[i].Body), Expression.Parameter(typeof(object)));
                }
                else
                {
                    x = Exprs[i];
                }
            }
            return x;
        }
        [System.Diagnostics.DebuggerStepThrough]
        public static Expression<Func<T, bool>> And<T>(params Expression<Func<T, bool>>[] Exprs)
        {
            var x = Exprs[0];
            for (var i = 1; i < Exprs.Length; i++)
            {
                if (x != null)
                {
                    x = Expression.Lambda<Func<T, bool>>(Expression.AndAlso(x.Body, Exprs[i].Body), Expression.Parameter(typeof(object)));
                }
                else
                {
                    x = Exprs[i];
                }
            }
            return x;
        }
        [System.Diagnostics.DebuggerStepThrough]
        internal static LambdaExpression CreateFieldExpr(string FieldName)
        {
            var cx = Expression.Call(typeof(Builder).GetMethod("Field"), Expression.Constant(FieldName));
            var ret = Expression.Lambda(cx, Expression.Parameter(typeof(object)));
            return ret;

        }
        [System.Diagnostics.DebuggerStepThrough]
        internal static LambdaExpression CreateFieldExprGetValue(LambdaExpression x)
        {
            var cx2 = Expression.MakeMemberAccess(x.Body, typeof(PField).GetProperty("Value"));
            return Expression.Lambda(cx2, Expression.Parameter(typeof(object)));

        }
        [System.Diagnostics.DebuggerStepThrough]
        internal static LambdaExpression CreateValue(object Value, Type DataType)
        {

            return Expression.Lambda(Expression.Convert(Expression.Constant(Value), DataType), Expression.Parameter(typeof(object)));

        }
        [System.Diagnostics.DebuggerStepThrough]
        public static Expression<Func<object, bool>> CreateExpr(string FieldName, string Op, object Value)
        {
            if (",==,!=,>,<,>=,<=,contains,first,last,".IndexOf("," + Op + ",") == -1)
            {
                throw new Exception($"'{Op}' is not in ==,!=,>,<,>=,<=,contains,first,last");
            }

            var f = CreateFieldExpr(FieldName);
            var fx = CreateFieldExprGetValue(f);
            var cx = CreateValue(Value, typeof(object));
            return CreateBx(fx, cx, Op);
        }
        [System.Diagnostics.DebuggerStepThrough]
        internal static Expression<Func<object, bool>> CreateBx(LambdaExpression Left, LambdaExpression Right, string Op)
        {
            if (Op == "==")
            {
                var bx = Expression.Equal(Left.Body, Right.Body);
                return Expression.Lambda<Func<object, bool>>(bx, Expression.Parameter(typeof(object)));
            }
            if (Op == "!=")
            {
                var bx = Expression.NotEqual(Left.Body, Right.Body);
                return Expression.Lambda<Func<object, bool>>(bx, Expression.Parameter(typeof(object)));
            }
            if (Op == ">")
            {
                var bx = Expression.GreaterThan(Left.Body, Right.Body);
                return Expression.Lambda<Func<object, bool>>(bx, Expression.Parameter(typeof(object)));
            }
            if (Op == ">=")
            {
                var bx = Expression.GreaterThanOrEqual(Left.Body, Right.Body);
                return Expression.Lambda<Func<object, bool>>(bx, Expression.Parameter(typeof(object)));
            }
            if (Op == "<")
            {
                var bx = Expression.LessThan(Left.Body, Right.Body);
                return Expression.Lambda<Func<object, bool>>(bx, Expression.Parameter(typeof(object)));
            }
            if (Op == "<=")
            {
                var bx = Expression.LessThanOrEqual(Left.Body, Right.Body);
                return Expression.Lambda<Func<object, bool>>(bx, Expression.Parameter(typeof(object)));
            }
            if (Op == "contains")
            {
                var mb = Expression.Lambda((Left.Body as MemberExpression).Expression, Expression.Parameter(typeof(object)));
                var mt = typeof(PField).GetMethod(nameof(PField.Contains));
                var lcx = CreateCall(mb, mt, Right.Body);
                var ret = Expression.Lambda<Func<object, bool>>(lcx.Body, Expression.Parameter(typeof(object)));
                return ret;

            }

            throw new NotImplementedException();
        }
        [System.Diagnostics.DebuggerStepThrough]
        internal static LambdaExpression CreateCall(LambdaExpression expr, MethodInfo method, params Expression[] args)
        {
            var cx = Expression.Call(expr.Body, method, args);
            return Expression.Lambda(cx, Expression.Parameter(typeof(object)));
        }
        [System.Diagnostics.DebuggerStepThrough]
        public static Expression<Func<object, bool>> CreateExpr(string FunctionCall, string FieldName, string Op, object Value)
        {

            var f = CreateFieldExpr(FieldName);
            if (FunctionCall == "day")
            {
                var cx = CreateCall(f, typeof(PField).GetMethod(nameof(PField.GetDay)));
                if (Value.GetType() != cx.ReturnType)
                {
                    throw new InvalidCastException($"Can not convert from {Value.GetType().FullName} to {cx.ReturnType.FullName}");
                }
                var vx = CreateValue(Value, cx.ReturnType);
                return CreateBx(cx, vx, Op);
            }
            if (FunctionCall == "month")
            {
                var cx = CreateCall(f, typeof(PField).GetMethod(nameof(PField.GetMonth)));
                if (Value.GetType() != cx.ReturnType)
                {
                    throw new InvalidCastException($"Can not convert from {Value.GetType().FullName} to {cx.ReturnType.FullName}");
                }
                var vx = CreateValue(Value, cx.ReturnType);
                return CreateBx(cx, vx, Op);
            }
            if (FunctionCall == "year")
            {
                var cx = CreateCall(f, typeof(PField).GetMethod(nameof(PField.GetYear)));
                if (Value.GetType() != cx.ReturnType)
                {
                    throw new InvalidCastException($"Can not convert from {Value.GetType().FullName} to {cx.ReturnType.FullName}");
                }
                var vx = CreateValue(Value, cx.ReturnType);
                return CreateBx(cx, vx, Op);
            }
            throw new NotImplementedException();
        }
        [System.Diagnostics.DebuggerStepThrough]
        private static CallFunction resovle_datetime_expr(MemberExpression Expr)
        {
            if (Expr.Member == typeof(DateTime).GetProperty(nameof(DateTime.Year)))
            {

                var field_path = Serilize(Expr.Expression);
                return new CallFunction
                {
                    FieldPath = field_path,
                    FuncName = "$$year"
                };


            }
            if (Expr.Member == typeof(DateTime).GetProperty(nameof(DateTime.Month)))
            {

                var field_path = Serilize(Expr.Expression);
                return new CallFunction
                {
                    FieldPath = field_path,
                    FuncName = "$$month"
                };


            }
            if (Expr.Member == typeof(DateTime).GetProperty(nameof(DateTime.Day)))
            {

                var field_path = Serilize(Expr.Expression);
                return new CallFunction
                {
                    FieldPath = field_path,
                    FuncName = "$$day"
                };


            }
            throw new NotSupportedException();
        }
        [System.Diagnostics.DebuggerStepThrough]
        private static bool IsMapping(Expression Expr, ref string FieldPath)
        {
            if (Expr is null) return false;
            if (Expr is MemberExpression)
            {
                var mExpr = Expr as MemberExpression;
                if (mExpr.Member.DeclaringType.Assembly == typeof(DataObjectMapping<object>).Assembly)
                {
                    if (mExpr.Member.Name == nameof(DataObjectMapping<object>.Fields))
                    {
                        var root_obj = LambdaExpression.Lambda(mExpr.Expression).Compile().DynamicInvoke();
                        if (root_obj is not null)
                        {
                            var r = root_obj.GetType().GetProperty("Root").GetValue(root_obj);
                            if (r != null && r.ToString() != "")
                            {
                                FieldPath = r.ToString() + FieldPath;
                                return true;
                            }
                        }
                        return true;
                    }
                }

                var ret = IsMapping(mExpr.Expression, ref FieldPath);
                if (mExpr.Expression.Type.GetProperty("Value") != mExpr.Member)
                {
                    FieldPath = FieldPath + "." + mExpr.Member.Name;
                }

                return ret;
            }
            return false;
        }
        [System.Diagnostics.DebuggerStepThrough]
        public static DataObjectMapping<T> DataObject<T>(string Root)
        {
            return new DataObjectMapping<T>(Root);
        }

        [System.Diagnostics.DebuggerStepThrough]
        private static object resolve(Expression x)
        {
            if (x is ConstantExpression)
            {
                return (x as ConstantExpression).Value;
            }
            if (x is MemberExpression && ((MemberExpression)x).Expression is UnaryExpression)
            {
                var ux = ((MemberExpression)x).Expression as UnaryExpression;
            }
            if (x is MemberExpression)
            {
                var mbx = x as MemberExpression;
                if (mbx.Expression is MemberExpression)
                {
                    var ref_feield = "";
                    var r = IsMapping(mbx, ref ref_feield);
                    if (r)
                    {
                        return ref_feield;

                    }
                    throw new NotImplementedException();
                }

                var objectMember = Expression.Convert(x, typeof(object));

                var getterLambda = Expression.Lambda<Func<object>>(objectMember);

                var getter = getterLambda.Compile();

                return getter();
            }
            if (x is NewArrayExpression)
            {
                var fx = x as NewArrayExpression;
                var ret = new List<object>();
                foreach (var m in fx.Expressions)
                {
                    ret.Add(resolve(m));
                }
                return ret.ToArray();
            }
            if (x.NodeType == ExpressionType.Convert)
            {
                return Expression.Lambda(x).Compile().DynamicInvoke();
            }
            if(x.NodeType== ExpressionType.Call)
            {

                var cx = x as MethodCallExpression;
                if(cx.Method== typeof(Builder).GetMethod(nameof(Builder.Boost)))
                {
                    var FieldName = resolve(cx.Arguments[0]);
                    var BoostValue = resolve(cx.Arguments[1]);
                    return $"{FieldName}^{BoostValue}";
                }
            }
            var ret_val = Expression.Lambda(x).Compile().DynamicInvoke();
            return ret_val;
        }
        [System.Diagnostics.DebuggerStepThrough]
        private static object GetOp(ExpressionType nodeType)
        {
            return expr_mapping[nodeType];
        }
    }
    public class FieldBuilder
    {
        public static PField Create(string Name)
        {
            return new PField(Name);
        }


    }
    public class PField
    {
        internal string name;

        public PField(string Name)
        {
            this.name = Name;
        }

        public object Value { get; }
        public bool Contains(object data)
        {
            throw new NotImplementedException("Just for expression");
        }

        public T GetValue<T>()
        {
            throw new NotImplementedException();
        }

        public int GetYear()
        {
            throw new NotImplementedException();
        }

        public int GetMonth()
        {
            throw new NotImplementedException();
        }
        public int GetDay()
        {
            throw new NotImplementedException();
        }

        public PField Boost(int BoostValue)
        {
            this.name = this.name.Split('^')[0] + "^" + BoostValue;
            return this;
        }
    }
    internal static class Ext
    {
        internal static PField ToField(this string owner)
        {
            return new PField(owner);
        }
    }
    internal class CallFunction
    {
        public object FieldPath { get; internal set; }
        public string FuncName { get; internal set; }
    }
    internal class CastFunctions
    {
        static internal bool Search(string Content, params string[] Fields)
        {
            return true;
        }
    }
}
 